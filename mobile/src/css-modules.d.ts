// Ambient declarations so TypeScript accepts the template's CSS imports.
// (Styles are resolved by Metro / NativeWind at build time, not by tsc.)
declare module '*.css';
declare module '*.module.css' {
  const classes: { [className: string]: string };
  export default classes;
}
