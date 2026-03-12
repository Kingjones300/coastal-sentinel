// =============================================================================
// COASTAL SENTINEL — Fig 2: FDI Detection Maps
// Google Earth Engine Script
// Produces: 4-panel publication figure (2 SCS + 2 BoB scenes)
// Target journal: Environmental Science & Technology (ES&T)
// Colour scheme: dark blue (#1B4F72) + orange (#E07B00)
// =============================================================================

// ─── STUDY REGION BOUNDS ─────────────────────────────────────────────────────
var SCS = ee.Geometry.Rectangle([100, 2, 122, 23]);
var BoB = ee.Geometry.Rectangle([80, 6, 100, 23]);

// ─── DATE RANGES FOR 2 SCENES PER REGION ─────────────────────────────────────
// Scene 1 = NE Monsoon (Jan–Mar) | Scene 2 = SW Monsoon (Jun–Aug)
// Adjust these dates to find cloud-free scenes in your area
var SCS_scene1_start = '2021-01-01';
var SCS_scene1_end   = '2021-03-31';
var SCS_scene2_start = '2021-06-01';
var SCS_scene2_end   = '2021-08-31';

var BoB_scene1_start = '2021-01-01';
var BoB_scene1_end   = '2021-03-31';
var BoB_scene2_start = '2021-06-01';
var BoB_scene2_end   = '2021-08-31';

// ─── BAND WAVELENGTHS (nm) — Sentinel-2 MSI ──────────────────────────────────
var lambda_RED  = 664.5;   // Band 4
var lambda_NIR  = 832.8;   // Band 8
var lambda_SWIR = 1613.7;  // Band 11

// ─── FDI COMPUTATION FUNCTION ─────────────────────────────────────────────────
// FDI = NIR − [RED + (SWIR − RED) × ((λNIR − λRED) / (λSWIR − λRED)) × 10]
// Cloud masking: SCL band values 4 (vegetation), 5 (bare soil), 6 (water) = valid
function computeFDI(image) {
  // Cloud mask using Scene Classification Layer
  var scl = image.select('SCL');
  var cloudMask = scl.eq(4).or(scl.eq(5)).or(scl.eq(6));
  
  // Scale reflectance from DN to [0,1]
  var RED  = image.select('B4').multiply(0.0001);
  var NIR  = image.select('B8').multiply(0.0001);
  var SWIR = image.select('B11').multiply(0.0001);
  
  // Wavelength interpolation coefficient
  var coeff = (lambda_NIR - lambda_RED) / (lambda_SWIR - lambda_RED);  // = 0.1024
  
  // FDI formula
  var FDI = NIR.subtract(
    RED.add(SWIR.subtract(RED).multiply(coeff).multiply(10))
  ).rename('FDI');
  
  return FDI.updateMask(cloudMask);
}

// ─── LOAD & PROCESS SENTINEL-2 COLLECTIONS ───────────────────────────────────
function getMedianFDI(region, startDate, endDate) {
  var collection = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
    .filterBounds(region)
    .filterDate(startDate, endDate)
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
    .map(computeFDI);
  
  var medianFDI = collection.median().clip(region);
  print('Scene count (', startDate, '):', collection.size());
  return medianFDI;
}

var FDI_SCS_1 = getMedianFDI(SCS, SCS_scene1_start, SCS_scene1_end);
var FDI_SCS_2 = getMedianFDI(SCS, SCS_scene2_start, SCS_scene2_end);
var FDI_BoB_1 = getMedianFDI(BoB, BoB_scene1_start, BoB_scene1_end);
var FDI_BoB_2 = getMedianFDI(BoB, BoB_scene2_start, BoB_scene2_end);

// ─── BINARY DETECTION MASK (FDI > 0.05) ──────────────────────────────────────
var THRESH = 0.05;
var DET_SCS_1 = FDI_SCS_1.gt(THRESH).selfMask();
var DET_SCS_2 = FDI_SCS_2.gt(THRESH).selfMask();
var DET_BoB_1 = FDI_BoB_1.gt(THRESH).selfMask();
var DET_BoB_2 = FDI_BoB_2.gt(THRESH).selfMask();

// ─── VISUALISATION PARAMETERS ─────────────────────────────────────────────────
// Continuous FDI: blue (low) → white (zero) → orange (high debris signal)
var fdiVis = {
  min: -0.05,
  max: 0.05,
  palette: ['#1B4F72', '#2980B9', '#FFFFFF', '#F39C12', '#E07B00']
};

// Binary detections: orange overlay on map
var detVis = {
  min: 0, max: 1,
  palette: ['#E07B00']
};

// ─── ADD LAYERS TO MAP ────────────────────────────────────────────────────────
// Panel (a): SCS NE Monsoon
Map.centerObject(SCS, 5);
Map.addLayer(FDI_SCS_1, fdiVis,  'Fig2a — SCS FDI (NE Monsoon Jan–Mar 2021)');
Map.addLayer(DET_SCS_1, detVis,  'Fig2a — SCS Detections > 0.05', false);
Map.addLayer(SCS, {color: '1B4F72'}, 'SCS Boundary', false, 0.5);

// Panel (b): SCS SW Monsoon
Map.addLayer(FDI_SCS_2, fdiVis,  'Fig2b — SCS FDI (SW Monsoon Jun–Aug 2021)');
Map.addLayer(DET_SCS_2, detVis,  'Fig2b — SCS Detections > 0.05', false);

// Panel (c): BoB NE Monsoon
Map.addLayer(FDI_BoB_1, fdiVis,  'Fig2c — BoB FDI (NE Monsoon Jan–Mar 2021)');
Map.addLayer(DET_BoB_1, detVis,  'Fig2c — BoB Detections > 0.05', false);
Map.addLayer(BoB, {color: 'E07B00'}, 'BoB Boundary', false, 0.5);

// Panel (d): BoB SW Monsoon
Map.addLayer(FDI_BoB_2, fdiVis,  'Fig2d — BoB FDI (SW Monsoon Jun–Aug 2021)');
Map.addLayer(DET_BoB_2, detVis,  'Fig2d — BoB Detections > 0.05', false);

print('✅ All 4 FDI panels computed. Use Export tasks below for 300 dpi TIFF export.');

// ─── EXPORT TO GOOGLE DRIVE (300 dpi equivalent = scale 30m) ─────────────────
// Export each panel as a GeoTIFF → assemble in Python (matplotlib) as Fig 2

Export.image.toDrive({
  image: FDI_SCS_1,
  description: 'Fig2a_SCS_FDI_NE_Monsoon',
  folder: 'CoastalSentinel_Fig2',
  fileNamePrefix: 'Fig2a_SCS_NE_Monsoon',
  region: SCS,
  scale: 500,          // 500m = regional overview; change to 100m for finer detail
  crs: 'EPSG:4326',
  maxPixels: 1e13
});

Export.image.toDrive({
  image: FDI_SCS_2,
  description: 'Fig2b_SCS_FDI_SW_Monsoon',
  folder: 'CoastalSentinel_Fig2',
  fileNamePrefix: 'Fig2b_SCS_SW_Monsoon',
  region: SCS,
  scale: 500,
  crs: 'EPSG:4326',
  maxPixels: 1e13
});

Export.image.toDrive({
  image: FDI_BoB_1,
  description: 'Fig2c_BoB_FDI_NE_Monsoon',
  folder: 'CoastalSentinel_Fig2',
  fileNamePrefix: 'Fig2c_BoB_NE_Monsoon',
  region: BoB,
  scale: 500,
  crs: 'EPSG:4326',
  maxPixels: 1e13
});

Export.image.toDrive({
  image: FDI_BoB_2,
  description: 'Fig2d_BoB_FDI_SW_Monsoon',
  folder: 'CoastalSentinel_Fig2',
  fileNamePrefix: 'Fig2d_BoB_SW_Monsoon',
  region: BoB,
  scale: 500,
  crs: 'EPSG:4326',
  maxPixels: 1e13
});

// =============================================================================
// AFTER EXPORT — run assemble_fig2.py (Python) to combine into final figure
// =============================================================================
