export default function (numerals) {
	return (value) => value.replace(/[0-9]/g, (i) => numerals[+i]);
}
