declare module 'georaster' {
    import { GeoRaster } from 'georaster-layer-for-leaflet';
    export default function parseGeoraster(data: any): Promise<GeoRaster>;
  }

  declare module 'georaster-layer-for-leaflet' {
    import { Layer } from 'leaflet';
    import { GeoRaster } from 'georaster';
  
    class GeoRasterLayer extends Layer {
      constructor(options: {
        georaster: GeoRaster;
        opacity?: number;
        pixelValuesToColorFn?: (values: number[]) => string;
        resolution?: number;
      });
    }
  
    export = GeoRasterLayer;
  }