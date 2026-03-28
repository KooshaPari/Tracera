// wraps: prop-types (via prop-types-real alias to bypass circular alias resolution)
// The prop-types alias points to this shim; to import the real package we use prop-types-real
import PropTypes, { checkPropTypes } from 'prop-types-real';

export { checkPropTypes };
export default PropTypes;
