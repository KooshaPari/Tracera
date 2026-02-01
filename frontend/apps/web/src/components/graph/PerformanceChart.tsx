import { memo, useEffect, useRef } from 'react';

interface PerformanceChartProps {
  fps: number;
  width?: number;
  height?: number;
}

export const PerformanceChart = memo(function PerformanceChart({
  fps,
  width = 200,
  height = 60,
}: PerformanceChartProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const historyRef = useRef<number[]>([]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Add to history
    historyRef.current.push(fps);
    if (historyRef.current.length > width) {
      historyRef.current.shift();
    }

    // Clear canvas
    ctx.clearRect(0, 0, width, height);

    // Draw grid lines
    ctx.strokeStyle = '#333';
    ctx.lineWidth = 1;
    for (let i = 0; i <= 60; i += 15) {
      const y = height - (i / 60) * height;
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(width, y);
      ctx.stroke();
    }

    // Draw FPS line
    ctx.strokeStyle = fps >= 55 ? '#10b981' : fps >= 30 ? '#f59e0b' : '#ef4444';
    ctx.lineWidth = 2;
    ctx.beginPath();

    historyRef.current.forEach((value, index) => {
      const x = index;
      const y = height - Math.min(value, 60) / 60 * height;

      if (index === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
    });

    ctx.stroke();

    // Draw current FPS text
    ctx.fillStyle = '#fff';
    ctx.font = '12px monospace';
    ctx.fillText(`${Math.round(fps)} FPS`, 4, 16);
  }, [fps, width, height]);

  return (
    <canvas
      ref={canvasRef}
      width={width}
      height={height}
      className="bg-background/90 rounded border"
    />
  );
});
