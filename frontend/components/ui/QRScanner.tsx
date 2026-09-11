"use client";

import { useEffect, useRef } from "react";
import jsQR from "jsqr";

interface QRScannerProps {
  onScan: (phone: string) => void;
  onClose: () => void;
}

export function QRScanner({ onScan, onClose }: QRScannerProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const onScanRef = useRef(onScan);

  useEffect(() => {
    onScanRef.current = onScan;
  });

  useEffect(() => {
    const video = videoRef.current!;
    const canvas = canvasRef.current!;
    const ctx = canvas.getContext("2d")!;
    let stream: MediaStream | null = null;
    let animationId: number | null = null;
    let active = true;

    async function start() {
      try {
        stream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: "environment", aspectRatio: 1 },
        });
      } catch {
        return;
      }
      if (!active) {
        stream.getTracks().forEach((t) => t.stop());
        return;
      }

      video.srcObject = stream;
      await video.play();

      function tick() {
        if (!active) return;
        if (video.readyState === video.HAVE_ENOUGH_DATA) {
          canvas.width = video.videoWidth;
          canvas.height = video.videoHeight;
          ctx.drawImage(video, 0, 0);
          const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
          const code = jsQR(imageData.data, imageData.width, imageData.height);
          if (code) {
            const phone = code.data.replace(/^yaqeen:\/\/pay\//, "");
            if (phone) onScanRef.current(phone);
          }
        }
        animationId = requestAnimationFrame(tick);
      }
      animationId = requestAnimationFrame(tick);
    }

    start();

    return () => {
      active = false;
      if (animationId !== null) cancelAnimationFrame(animationId);
      if (stream) stream.getTracks().forEach((t) => t.stop());
      video.srcObject = null;
    };
  }, []);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-navy/80 px-4">
      <div className="bg-white w-full max-w-sm overflow-hidden rounded-xl">
        <div className="flex items-center justify-between px-4 py-3 border-b border-sage-mid">
          <p className="text-sm font-semibold text-navy">Scan QR Code</p>
          <button
            type="button"
            onClick={onClose}
            className="text-navy-muted active:opacity-60"
            aria-label="Close scanner"
          >
            <svg
              className="h-5 w-5"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M18 6 6 18" />
              <path d="m6 6 12 12" />
            </svg>
          </button>
        </div>
        <div className="p-4">
          <div className="relative w-full aspect-square">
            <video
              ref={videoRef}
              className="absolute inset-0 w-full h-full object-cover"
              playsInline
              muted
            />
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="relative w-3/5 aspect-square">
                <span className="absolute top-0 left-0 w-6 h-6 border-t-2 border-l-2 border-white" />
                <span className="absolute top-0 right-0 w-6 h-6 border-t-2 border-r-2 border-white" />
                <span className="absolute bottom-0 left-0 w-6 h-6 border-b-2 border-l-2 border-white" />
                <span className="absolute bottom-0 right-0 w-6 h-6 border-b-2 border-r-2 border-white" />
              </div>
            </div>
          </div>
          <canvas ref={canvasRef} className="hidden" />
          <p className="text-xs text-navy-muted text-center mt-3">
            Point your camera at a Yaqeen QR code
          </p>
        </div>
      </div>
    </div>
  );
}
