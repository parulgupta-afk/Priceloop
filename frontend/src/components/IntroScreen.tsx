import React, { useEffect, useRef } from 'react';
import { ArrowRight } from 'lucide-react';

interface IntroScreenProps {
  onEnterDashboard?: () => void;
  onSkip?: () => void;
}

export const IntroScreen: React.FC<IntroScreenProps> = ({
  onEnterDashboard,
  onSkip,
}) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [isRevealed, setIsRevealed] = React.useState(false);
  const [isReadyToEnter, setIsReadyToEnter] = React.useState(false);

  const handleProceed = () => {
    if (onEnterDashboard) {
      onEnterDashboard();
    } else if (onSkip) {
      onSkip();
    }
  };

  useEffect(() => {
    // Trigger animation after brief delay
    const revealTimer = setTimeout(() => {
      setIsRevealed(true);
    }, 600);

    const readyTimer = setTimeout(() => {
      setIsReadyToEnter(true);
    }, 1800);

    // Auto-advance to dashboard after intro plays
    const autoAdvanceTimer = setTimeout(() => {
      handleProceed();
    }, 3200);

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Enter' || e.key === ' ' || e.key === 'Escape') {
        handleProceed();
      }
    };

    window.addEventListener('keydown', handleKeyDown);

    return () => {
      clearTimeout(revealTimer);
      clearTimeout(readyTimer);
      clearTimeout(autoAdvanceTimer);
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [onEnterDashboard, onSkip]);

  // WebGL Shader Animation
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    let animationFrameId: number;
    const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
    if (!gl) return;

    const syncSize = () => {
      if (!canvas) return;
      const w = window.innerWidth || 1280;
      const h = window.innerHeight || 720;
      if (canvas.width !== w || canvas.height !== h) {
        canvas.width = w;
        canvas.height = h;
      }
    };

    syncSize();
    window.addEventListener('resize', syncSize);

    const vs = `
      attribute vec2 a_position;
      varying vec2 v_texCoord;
      void main() {
        v_texCoord = a_position * 0.5 + 0.5;
        gl_Position = vec4(a_position, 0.0, 1.0);
      }
    `;

    const fs = `
      precision highp float;
      uniform float u_time;
      uniform vec2 u_resolution;
      void main() {
        vec2 uv = gl_FragCoord.xy / u_resolution.xy;
        uv = uv * 2.0 - 1.0;
        uv.x *= u_resolution.x / u_resolution.y;
        float noise = sin(uv.x * 3.0 + u_time) * cos(uv.y * 3.0 - u_time * 0.5);
        noise += sin(uv.y * 5.0 + u_time * 0.8) * cos(uv.x * 2.0 + u_time * 0.3);
        vec3 color1 = vec3(0.059, 0.090, 0.165); 
        vec3 color2 = vec3(0.15, 0.25, 0.45);   
        vec3 finalColor = mix(color1, color2, noise * 0.5 + 0.5);
        finalColor += 0.05 * sin(u_time + uv.x * 10.0); 
        gl_FragColor = vec4(finalColor, 1.0);
      }
    `;

    const createShader = (type: number, src: string) => {
      const s = gl.createShader(type);
      if (!s) return null;
      gl.shaderSource(s, src);
      gl.compileShader(s);
      return s;
    };

    const vertexShader = createShader(gl.VERTEX_SHADER, vs);
    const fragmentShader = createShader(gl.FRAGMENT_SHADER, fs);
    if (!vertexShader || !fragmentShader) return;

    const prog = gl.createProgram();
    if (!prog) return;
    gl.attachShader(prog, vertexShader);
    gl.attachShader(prog, fragmentShader);
    gl.linkProgram(prog);
    gl.useProgram(prog);

    const buf = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, buf);
    gl.bufferData(
      gl.ARRAY_BUFFER,
      new Float32Array([-1, -1, 1, -1, -1, 1, 1, 1]),
      gl.STATIC_DRAW
    );

    const pos = gl.getAttribLocation(prog, 'a_position');
    gl.enableVertexAttribArray(pos);
    gl.vertexAttribPointer(pos, 2, gl.FLOAT, false, 0, 0);

    const uTime = gl.getUniformLocation(prog, 'u_time');
    const uRes = gl.getUniformLocation(prog, 'u_resolution');

    const render = (t: number) => {
      syncSize();
      gl.viewport(0, 0, canvas.width, canvas.height);
      if (uTime) gl.uniform1f(uTime, t * 0.001);
      if (uRes) gl.uniform2f(uRes, canvas.width, canvas.height);
      gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
      animationFrameId = requestAnimationFrame(render);
    };

    animationFrameId = requestAnimationFrame(render);

    return () => {
      window.removeEventListener('resize', syncSize);
      cancelAnimationFrame(animationFrameId);
    };
  }, []);

  return (
    <div
      id="intro-screen"
      className="fixed inset-0 w-screen h-screen overflow-hidden z-50 flex flex-col items-center justify-center bg-[#0b1c30] text-white select-none"
    >
      {/* Background Canvas Shader */}
      <div className="absolute inset-0 w-full h-full z-0">
        <canvas ref={canvasRef} className="w-full h-full block" />
      </div>

      {/* Top Brand Logo */}
      <header className="absolute top-0 left-0 w-full p-8 z-20 flex justify-between items-start animate-fade-in">
        <div className="flex items-center gap-3">
          <img
            alt="Priceloop Logo"
            className="h-9 w-auto rounded-sm mix-blend-screen opacity-90 invert brightness-200 grayscale"
            src="https://lh3.googleusercontent.com/aida/AEtjO1WQeqo6ixOTLdiEF8WsqcpSE05ALFPy_50Qf7a7m4nLgudZXyVHq3vBpIYIBNIjPeXbr27D0kplf29DB2KNZLVyrjXL5ees3VfuoXCH5NljZeCDv7qbM5H0oP3ziEXMRCGVckOP2max54Vt391XrDr3pHVZUq5rCz-bIvcI95arFOo4tkbFhZldYDRZujo5rc-y02hTJw-PcbMLAoqJ55dOGJdnhPZg11YFNF9fUwJNAq4fi0o5Drl4PQ4"
          />
        </div>
      </header>

      {/* Central Cinematic Animation */}
      <main className="relative z-10 w-full h-full flex flex-col items-center justify-center pointer-events-none">
        <div
          ref={containerRef}
          className="relative inline-flex overflow-hidden items-center justify-center h-48 md:h-64 w-full"
        >
          {/* Initial Monogram P */}
          <span
            className={`inline-block font-black text-white text-[120px] md:text-[200px] leading-none transition-all duration-1000 ease-in-out ${
              isRevealed
                ? '-translate-x-[150vw] opacity-0'
                : 'translate-x-[45%] opacity-100'
            }`}
            style={{ fontFamily: 'Inter, sans-serif' }}
          >
            P
          </span>

          {/* Initial Monogram L */}
          <span
            className={`inline-block font-black text-white text-[120px] md:text-[200px] leading-none transition-all duration-1000 ease-in-out ${
              isRevealed
                ? 'translate-x-[150vw] scale-x-[-1] opacity-0'
                : '-translate-x-[45%] scale-x-[-1] opacity-100'
            }`}
            style={{ fontFamily: 'Inter, sans-serif' }}
          >
            L
          </span>

          {/* Final Expanded Full Word */}
          <span
            className={`absolute whitespace-nowrap font-extrabold text-white tracking-tight transition-all duration-700 ease-out text-5xl md:text-8xl ${
              isRevealed
                ? 'opacity-100 scale-100 animate-pulse-subtle'
                : 'opacity-0 scale-95'
            }`}
            style={{ fontFamily: 'Inter, sans-serif' }}
          >
            Priceloop
          </span>
        </div>

        <div
          className={`mt-8 text-white/80 font-mono tracking-widest uppercase text-xs md:text-sm text-center max-w-md px-4 drop-shadow-md transition-opacity duration-1000 ${
            isRevealed ? 'opacity-100' : 'opacity-0'
          }`}
        >
          Intelligence Platform Initiating...
        </div>
      </main>

      {/* Skip / Enter Action Button */}
      <div className="absolute bottom-8 right-8 z-30">
        <button
          id="skip-intro-button"
          onClick={(e) => {
            e.stopPropagation();
            handleProceed();
          }}
          className="flex items-center gap-2 px-6 py-3 rounded-full bg-white/15 hover:bg-white/25 active:scale-95 transition-all text-white font-mono text-sm group shadow-xl backdrop-blur-md border border-white/30 cursor-pointer"
        >
          <span>{isReadyToEnter ? 'ENTER DASHBOARD' : 'SKIP'}</span>
          <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
        </button>
      </div>
    </div>
  );
};
