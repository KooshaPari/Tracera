import { expectDeprecated, expectType } from "tsd";
import uri, {
	type Options,
	type options,
	type URIComponent,
	type URIComponents,
} from "..";

const parsed = uri.parse("foo");
expectType<URIComponents>(parsed);
const parsed2 = uri.parse("foo", {
	domainHost: true,
	scheme: "https",
	unicodeSupport: false,
});
expectType<URIComponents>(parsed2);

expectType<URIComponent>({} as URIComponents);
expectDeprecated({} as URIComponents);

expectType<Options>({} as options);
expectDeprecated({} as options);
