import React from 'react';

interface SliderProps {
  label: string;
  value: number;
  min: number;
  max: number;
  step?: number;
  unit?: string;
  onChange: (val: number) => void;
}

export const Slider = ({ label, value, min, max, step = 1, unit = "", onChange }: SliderProps) => (
  <div className="space-y-3">
    <div className="flex justify-between">
      <label className="text-sm font-medium text-gray-700">{label}</label>
      <span className="text-sm font-bold text-[#001D3D]">{value.toLocaleString()} {unit}</span>
    </div>
    <input
      type="range"
      min={min}
      max={max}
      step={step}
      value={value}
      onChange={(e) => onChange(Number(e.target.value))}
      className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-[#FFD700]"
    />
  </div>
);
