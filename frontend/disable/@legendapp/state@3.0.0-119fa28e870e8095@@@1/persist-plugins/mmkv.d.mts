import { Change } from '@legendapp/state';
import { ObservablePersistPlugin, PersistOptions, PersistMetadata } from '@legendapp/state/sync';
import * as mmkv from 'react-native-mmkv';

type Configuration = mmkv.Configuration;
declare class ObservablePersistMMKV implements ObservablePersistPlugin {
    private data;
    private storages;
    private configuration;
    constructor(configuration: Configuration);
    getTable<T = any>(table: string, init: object, config: PersistOptions): T;
    getMetadata(table: string, config: PersistOptions): PersistMetadata;
    set(table: string, changes: Change[], config: PersistOptions): void;
    setMetadata(table: string, metadata: PersistMetadata, config: PersistOptions): Promise<void>;
    deleteTable(table: string, config: PersistOptions): void;
    deleteMetadata(table: string, config: PersistOptions): void;
    private getStorage;
    private setValue;
    private save;
}
declare function observablePersistMMKV(configuration: Configuration): ObservablePersistMMKV;

export { ObservablePersistMMKV, observablePersistMMKV };
