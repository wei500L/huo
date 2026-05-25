export function CameraPlaceholder() {
  return (
    <div className="relative h-[240px] w-full max-w-[320px] border-2 border-stroke-ink bg-panel-dim shadow-hard">
      {/* TODO 22: v1 only renders a placeholder, no getUserMedia. */}
      <div className="absolute left-2 right-2 top-2 flex items-start justify-between text-[10px] leading-none">
        <span className="animate-pulse font-retro text-pixel-red">REC</span>
      </div>

      <div className="flex h-full items-center justify-center px-4 text-center">
        <p className="text-[16px] leading-none text-ink-2">摄像头流未接入后端</p>
      </div>
    </div>
  );
}

export default CameraPlaceholder;
