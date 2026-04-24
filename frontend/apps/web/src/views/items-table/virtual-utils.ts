function createVirtualContainerStyle(totalSize: number): React.CSSProperties {
  return {
    height: `${totalSize}px`,
    position: 'relative',
    width: '100%',
  };
}

function createVirtualRowStyle(size: number, start: number): React.CSSProperties {
  return {
    height: `${size}px`,
    left: 0,
    position: 'absolute',
    top: 0,
    transform: `translateY(${start}px)`,
    width: '100%',
  };
}

export { createVirtualContainerStyle, createVirtualRowStyle };
