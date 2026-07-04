import fg from 'fast-glob';
import fs from 'node:fs';
import path from 'node:path';
import { Project, Node } from 'ts-morph';

const ROOT = process.cwd();
const SCOPE_DIRS = ['apps', 'packages'];
const INDEX_RE = /(?:^|[\\/])index\\.(ts|tsx)$/;
const EXTENSIONS = ['.ts', '.tsx', '.js', '.jsx'];

const unresolved: string[] = [];
const deleted: string[] = [];
const unsupported: string[] = [];

const project = new Project({
  tsConfigFilePath: path.join(ROOT, 'apps/web/tsconfig.json'),
  skipAddingFilesFromTsConfig: true,
});

project.addSourceFilesAtPaths([
  'apps/**/*.ts',
  'apps/**/*.tsx',
  'packages/**/*.ts',
  'packages/**/*.tsx',
]);

function resolveModule(fromDir: string, moduleSpec: string): string | null {
  if (!moduleSpec.startsWith('.')) {
    return null;
  }
  const base = path.resolve(fromDir, moduleSpec);
  for (const ext of EXTENSIONS) {
    const candidate = `${base}${ext}`;
    if (fs.existsSync(candidate)) return candidate;
  }
  if (fs.existsSync(base) && fs.statSync(base).isDirectory()) {
    for (const ext of EXTENSIONS) {
      const candidate = path.join(base, `index${ext}`);
      if (fs.existsSync(candidate)) return candidate;
    }
  }
  return null;
}

function toModuleSpec(fromFile: string, targetFile: string): string {
  const rel = path.relative(path.dirname(fromFile), targetFile);
  const normalized = rel.split(path.sep).join('/');
  const withoutExt = normalized.replace(/\\.(ts|tsx|js|jsx)$/, '');
  return withoutExt.startsWith('.') ? withoutExt : `./${withoutExt}`;
}

type ExportInfo = {
  moduleSpec: string;
  moduleTarget: string;
  isDefault: boolean;
  isTypeOnly: boolean;
  isExternal: boolean;
};

type BarrelInfo = {
  indexPath: string;
  exportMap: Map<string, ExportInfo[]>;
  hasNamespaceExport: boolean;
};

function getExportedNamesFromFile(sourcePath: string): string[] {
  const sourceFile = project.getSourceFile(sourcePath);
  if (!sourceFile) return [];
  const exported = sourceFile.getExportedDeclarations();
  return Array.from(exported.keys());
}

function buildBarrelInfo(indexPath: string): BarrelInfo | null {
  const sourceFile = project.getSourceFile(indexPath);
  if (!sourceFile) return null;

  const statements = sourceFile.getStatements();
  const hasNonExport = statements.some((stmt) => {
    return !Node.isExportDeclaration(stmt) && !Node.isExportAssignment(stmt);
  });
  if (hasNonExport) {
    return null;
  }
  if (sourceFile.getExportAssignments().length > 0) {
    return null;
  }

  const exportMap = new Map<string, ExportInfo[]>();
  let hasNamespaceExport = false;
  const indexDir = path.dirname(indexPath);

  const starExports: string[] = [];

  for (const decl of sourceFile.getExportDeclarations()) {
    const moduleSpec = decl.getModuleSpecifierValue();
    if (!moduleSpec) {
      return null;
    }

    const isExternal = !moduleSpec.startsWith('.');
    const moduleAbs = isExternal ? null : resolveModule(indexDir, moduleSpec);
    if (!isExternal && !moduleAbs) {
      unresolved.push(`${indexPath} cannot resolve module ${moduleSpec}`);
      continue;
    }

    const namespaceExport = decl.getNamespaceExport();
    if (namespaceExport) {
      hasNamespaceExport = true;
      const name = namespaceExport.getName();
      if (isExternal) {
        unsupported.push(`${indexPath} uses namespace export from external module ${moduleSpec}`);
        return null;
      }
      const info: ExportInfo = {
        moduleSpec,
        moduleTarget: moduleAbs ?? moduleSpec,
        isDefault: false,
        isTypeOnly: decl.isTypeOnly(),
        isExternal,
      };
      exportMap.set(name, [info]);
      continue;
    }

    const namedExports = decl.getNamedExports();
    if (namedExports.length === 0) {
      if (isExternal) {
        unsupported.push(`${indexPath} re-exports * from external module ${moduleSpec}`);
        return null;
      }
      starExports.push(moduleSpec);
      continue;
    }

    for (const spec of namedExports) {
      const name = spec.getName();
      const alias = spec.getAliasNode()?.getText();
      const exportName = alias ?? name;
      const info: ExportInfo = {
        moduleSpec,
        moduleTarget: moduleAbs ?? moduleSpec,
        isDefault: name === 'default',
        isTypeOnly: decl.isTypeOnly(),
        isExternal,
      };
      const bucket = exportMap.get(exportName) ?? [];
      bucket.push(info);
      exportMap.set(exportName, bucket);
    }
  }

  for (const moduleSpec of starExports) {
    const moduleAbs = resolveModule(indexDir, moduleSpec);
    if (!moduleAbs) {
      unresolved.push(`${indexPath} cannot resolve module ${moduleSpec}`);
      continue;
    }
    const exportedNames = getExportedNamesFromFile(moduleAbs);
    for (const exportName of exportedNames) {
      if (exportName === 'default') {
        continue;
      }
      const info: ExportInfo = {
        moduleSpec,
        moduleTarget: moduleAbs,
        isDefault: false,
        isTypeOnly: false,
        isExternal: false,
      };
      const bucket = exportMap.get(exportName) ?? [];
      bucket.push(info);
      exportMap.set(exportName, bucket);
    }
  }

  return { indexPath, exportMap, hasNamespaceExport };
}

async function findIndexFiles(): Promise<string[]> {
  const patterns = SCOPE_DIRS.map((dir) => `${dir}/**/index.{ts,tsx}`);
  return fg(patterns, {
    cwd: ROOT,
    absolute: true,
    dot: false,
    ignore: [
      '**/node_modules/**',
      '**/dist/**',
      '**/storybook-static/**',
      '**/.turbo/**',
      '**/.git/**',
    ],
  });
}

const indexFiles = await findIndexFiles();
const barrelMap = new Map<string, BarrelInfo>();

for (const indexPath of indexFiles) {
  const info = buildBarrelInfo(indexPath);
  if (info) barrelMap.set(indexPath, info);
}

if (unsupported.length > 0) {
  console.error('Unsupported barrel files:');
  unsupported.forEach((entry) => console.error(`  - ${entry}`));
  process.exit(1);
}

function resolveIndexForImport(importingFile: string, moduleSpec: string): BarrelInfo | null {
  if (!moduleSpec.startsWith('.')) return null;
  const abs = path.resolve(path.dirname(importingFile), moduleSpec);
  const candidates: string[] = [];
  if (INDEX_RE.test(abs)) {
    candidates.push(abs);
  } else if (fs.existsSync(abs) && fs.statSync(abs).isDirectory()) {
    for (const ext of EXTENSIONS) {
      candidates.push(path.join(abs, `index${ext}`));
    }
  } else {
    for (const ext of EXTENSIONS) {
      candidates.push(`${abs}${ext}`);
    }
  }

  for (const candidate of candidates) {
    if (barrelMap.has(candidate)) {
      return barrelMap.get(candidate) ?? null;
    }
  }
  return null;
}

for (const sourceFile of project.getSourceFiles()) {
  const filePath = sourceFile.getFilePath();
  if (!SCOPE_DIRS.some((dir) => filePath.includes(`${path.sep}${dir}${path.sep}`))) {
    continue;
  }

  const imports = sourceFile.getImportDeclarations();
  for (const importDecl of imports) {
    const moduleSpec = importDecl.getModuleSpecifierValue();
    const barrel = resolveIndexForImport(filePath, moduleSpec);
    if (!barrel) continue;

    if (barrel.hasNamespaceExport && importDecl.getNamespaceImport()) {
      unresolved.push(`${filePath} uses namespace import from ${moduleSpec}`);
      continue;
    }

    const exportMap = barrel.exportMap;
    const typeImports = new Map<string, { name: string; alias?: string }[]>();
    const valueImports = new Map<string, { name: string; alias?: string }[]>();
    const defaultImports = new Map<string, string>();
    const externalModules = new Set<string>();

    const typeOnlyImport = importDecl.isTypeOnly();
    const defaultImport = importDecl.getDefaultImport();
    if (defaultImport) {
      const exportInfos = exportMap.get('default');
      if (!exportInfos || exportInfos.length === 0) {
        unresolved.push(`${filePath} default import from ${moduleSpec} cannot be resolved`);
        continue;
      }
      const info = exportInfos[0];
      defaultImports.set(info.moduleTarget, defaultImport.getText());
      if (info.isExternal) externalModules.add(info.moduleTarget);
    }

    const namespaceImport = importDecl.getNamespaceImport();
    if (namespaceImport) {
      unresolved.push(`${filePath} namespace import from ${moduleSpec} cannot be resolved`);
      continue;
    }

    for (const named of importDecl.getNamedImports()) {
      const name = named.getName();
      const alias = named.getAliasNode()?.getText();
      const exportInfos = exportMap.get(name);
      if (!exportInfos || exportInfos.length === 0) {
        unresolved.push(`${filePath} cannot resolve ${name} from ${moduleSpec}`);
        continue;
      }
      const info = exportInfos[0];
      const bucket =
        named.isTypeOnly() || typeOnlyImport || info.isTypeOnly ? typeImports : valueImports;
      const list = bucket.get(info.moduleTarget) ?? [];
      list.push({ name, alias });
      bucket.set(info.moduleTarget, list);
      if (info.isExternal) externalModules.add(info.moduleTarget);
    }

    const newImports: {
      moduleSpec: string;
      isTypeOnly: boolean;
      defaultImport?: string;
      named?: { name: string; alias?: string }[];
    }[] = [];

    for (const [moduleTarget, defaultName] of defaultImports.entries()) {
      const moduleSpecOut = externalModules.has(moduleTarget)
        ? moduleTarget
        : toModuleSpec(filePath, moduleTarget);
      const namedList = valueImports.get(moduleTarget) ?? [];
      newImports.push({
        moduleSpec: moduleSpecOut,
        isTypeOnly: false,
        defaultImport: defaultName,
        named: namedList,
      });
      valueImports.delete(moduleTarget);
    }

    for (const [moduleTarget, namedList] of valueImports.entries()) {
      const moduleSpecOut = externalModules.has(moduleTarget)
        ? moduleTarget
        : toModuleSpec(filePath, moduleTarget);
      newImports.push({ moduleSpec: moduleSpecOut, isTypeOnly: false, named: namedList });
    }

    for (const [moduleTarget, namedList] of typeImports.entries()) {
      const moduleSpecOut = externalModules.has(moduleTarget)
        ? moduleTarget
        : toModuleSpec(filePath, moduleTarget);
      newImports.push({ moduleSpec: moduleSpecOut, isTypeOnly: true, named: namedList });
    }

    if (newImports.length === 0) {
      unresolved.push(`${filePath} import from ${moduleSpec} could not be rewritten`);
      continue;
    }

    const insertIndex = importDecl.getChildIndex();
    importDecl.remove();

    for (const entry of newImports) {
      sourceFile.insertImportDeclaration(insertIndex, {
        moduleSpecifier: entry.moduleSpec,
        defaultImport: entry.defaultImport,
        namedImports: entry.named?.map((spec) => ({
          name: spec.name,
          alias: spec.alias,
        })),
        isTypeOnly: entry.isTypeOnly,
      });
    }
  }
}

if (unresolved.length > 0) {
  console.error('Unresolved barrel imports:');
  unresolved.forEach((entry) => console.error(`  - ${entry}`));
  process.exit(1);
}

project.saveSync();

for (const indexPath of barrelMap.keys()) {
  try {
    fs.unlinkSync(indexPath);
    deleted.push(indexPath);
  } catch (err) {
    console.error(`Failed to delete ${indexPath}:`, err);
    process.exit(1);
  }
}

console.log(`Removed ${deleted.length} barrel files.`);
