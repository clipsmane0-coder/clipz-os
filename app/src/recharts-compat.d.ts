// ============================================================
// Recharts + React 19 Type Compatibility Shim
// ============================================================
// Recharts v2.x components extend React.Component with a
// constructor signature that React 19 types no longer accept.
// This module augmentation patches the JSX element types for
// all recharts component exports so they pass type-check.
//
// Remove when upgrading to recharts v3.x (which natively
// supports React 19 typing).
// ============================================================

import "recharts";

declare module "recharts" {
  // Patch the core Recharts SVG component types to be
  // valid JSX element constructors for React 19.
  interface RechartsComponentClass {
    new (props: any): React.Component<any, any, any>;
  }

  export const Area: RechartsComponentClass;
  export const Bar: RechartsComponentClass;
  export const Line: React.FC<any>;
  export const Pie: RechartsComponentClass;
  export const Cell: React.FC<any>;
  export const XAxis: RechartsComponentClass;
  export const YAxis: RechartsComponentClass;
  export const Tooltip: RechartsComponentClass;
  export const CartesianGrid: React.FC<any>;
  export const Legend: React.FC<any>;
  export const ResponsiveContainer: React.FC<any>;
  export const AreaChart: React.FC<any>;
  export const BarChart: React.FC<any>;
  export const LineChart: React.FC<any>;
  export const PieChart: React.FC<any>;
  export const RadarChart: React.FC<any>;
  export const Radar: RechartsComponentClass;
  export const PolarGrid: React.FC<any>;
  export const PolarAngleAxis: RechartsComponentClass;
  export const PolarRadiusAxis: RechartsComponentClass;
}
