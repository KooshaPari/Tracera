import { memo, useEffect, useRef } from 'react';

const FPS_GOOD = 55;
const FPS_WARN = 30;
const FPS_MAX = 60;
const GRID_STEP = 15;
const FONT_SIZE = 12;
const TEXT_OFFSET_X = 4;
const TEXT_OFFSET_Y = 16;
const LINE_WIDTH_THIN = 1;
const LINE_WIDTH_THICK = 2;

interface PerformanceChartProps {
  fps: number;
  height?: number;
  width?: number;
}

const drawGridLines = (ctx: CanvasRenderingContext2D, width: number, height: number) => {
  ctx.strokeStyle = '#333';
  ctx.lineWidth = LINE_WIDTH_THIN;
  for (let i = 0; i <= FPS_MAX; i += GRID_STEP) {
    const y = height - (i / FPS_MAX) * height;
    ctx.beginPath();
    ctx.moveTo(0, y);
    ctx.lineTo(width, y);
    ctx.stroke();
  }
};

const drawFpsLine = (
  ctx: CanvasRenderingContext2D,
  history: number[],
  _width: number,
  height: number,
  fps: number,
) => {
  ctx.strokeStyle = fps >= FPS_GOOD ? '#10b981' : fps >= FPS_WARN ? '#f59e0b' : '#ef4444';
  ctx.lineWidth = LINE_WIDTH_THICK;
  ctx.beginPath();
  history.forEach((value, index) => {
    const x = index;
    const y = height - (Math.min(value, FPS_MAX) / FPS_MAX) * height;
    if (index === 0) {
      ctx.moveTo(x, y);
    } else {
      ctx.lineTo(x, y);
    }
  });
  ctx.stroke();
  ctx.fillStyle = '#fff';
  ctx.font = `${FONT_SIZE}px monospace`;
  ctx.fillText(`${Math.round(fps)} FPS`, TEXT_OFFSET_X, TEXT_OFFSET_Y);
};

export const PerformanceChart = memo(function PerformanceChart({
  fps,
  width = 200,
  height = 60,
}: PerformanceChartProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const historyRef = useRef<number[]>([]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) {
      return;
    }

    const ctx = canvas.getContext('2d');
    if (!ctx) {
      return;
    }

    historyRef.current.push(fps);
    if (historyRef.current.length > width) {
      historyRef.current.shift();
    }

    ctx.clearRect(0, 0, width, height);
    drawGridLines(ctx, width, height);
    drawFpsLine(ctx, historyRef.current, width, height, fps);
  }, [fps, width, height]);

  return (
    <canvas
      ref={canvasRef}
      width={width}
      height={height}
      className='bg-background/90 rounded border'
    />
  );
});
