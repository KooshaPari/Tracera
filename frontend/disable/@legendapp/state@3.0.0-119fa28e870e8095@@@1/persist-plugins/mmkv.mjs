import { setAtPath, internal } from '@legendapp/state';
import * as mmkv from 'react-native-mmkv';

// src/persist-plugins/mmkv.ts
var symbolDefault = Symbol();
var MetadataSuffix = "__m";
var { safeParse, safeStringify } = internal;
function createMMKVInstance(config) {
  const hasCreateFunction = "createMMKV" in mmkv;
  if (hasCreateFunction) {
    return mmkv.createMMKV(config);
  } else {
    const { MMKV: MMKVConstructor } = mmkv;
    return new MMKVConstructor(config);
  }
}
function deleteFromMMKV(storage, key) {
  if ("remove" in storage) {
    storage.remove(key);
  } else {
    storage.delete(key);
  }
}
var ObservablePersistMMKV = class {
  constructor(configuration) {
    this.data = {};
    this.storages = /* @__PURE__ */ new Map([
      [
        symbolDefault,
        createMMKVInstance({
          id: `obsPersist`
        })
      ]
    ]);
    this.configuration = configuration;
  }
  // Gets
  getTable(table, init, config) {
    const storage = this.getStorage(config);
    if (this.data[table] === void 0) {
      try {
        const value = storage.getString(table);
        this.data[table] = value ? safeParse(value) : init;
      } catch (e) {
        console.error("[legend-state] MMKV failed to parse", table);
      }
    }
    return this.data[table];
  }
  getMetadata(table, config) {
    return this.getTable(table + MetadataSuffix, {}, config);
  }
  // Sets
  set(table, changes, config) {
    if (!this.data[table]) {
      this.data[table] = {};
    }
    for (let i = 0; i < changes.length; i++) {
      const { path, valueAtPath, pathTypes } = changes[i];
      this.data[table] = setAtPath(this.data[table], path, pathTypes, valueAtPath);
    }
    this.save(table, config);
  }
  setMetadata(table, metadata, config) {
    return this.setValue(table + MetadataSuffix, metadata, config);
  }
  deleteTable(table, config) {
    const storage = this.getStorage(config);
    delete this.data[table];
    deleteFromMMKV(storage, table);
  }
  deleteMetadata(table, config) {
    this.deleteTable(table + MetadataSuffix, config);
  }
  // Private
  getStorage(config) {
    const configuration = config.mmkv || this.configuration;
    if (configuration) {
      const key = JSON.stringify(configuration);
      let storage = this.storages.get(key);
      if (!storage) {
        storage = createMMKVInstance(configuration);
        this.storages.set(key, storage);
      }
      return storage;
    } else {
      return this.storages.get(symbolDefault);
    }
  }
  async setValue(table, value, config) {
    this.data[table] = value;
    this.save(table, config);
  }
  save(table, config) {
    const storage = this.getStorage(config);
    const v = this.data[table];
    if (v !== void 0) {
      try {
        storage.set(table, safeStringify(v));
      } catch (err) {
        console.error(err);
      }
    } else {
      deleteFromMMKV(storage, table);
    }
  }
};
function observablePersistMMKV(configuration) {
  return new ObservablePersistMMKV(configuration);
}

export { ObservablePersistMMKV, observablePersistMMKV };
