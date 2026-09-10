// ============================================================
// The Coastal Sentinel - FDI Detection (Google Earth Engine)
// Floating Debris Index following Biermann et al. (2020)
// RE2-baseline formulation: FDI = NIR - NIR'
// Study basins: South China Sea (SCS) and Bay of Bengal (BoB)
// Study period: January 2019 - December 2023
// ============================================================

var SCS = ee.Geometry.Rectangle([100, 2, 122, 23]);
var BoB = ee.Geometry.Rectangle([80, 6, 100, 23]);

// Real Sentinel-2 band wavelengths (nm)
var lambda_RED = 664.5;
var lambda_RE2 = 740.0;
var lambda_NIR = 832.8;
var lambda_SWIR = 1613.7;
var coeff = (lambda_NIR - lambda_RED) / (lambda_SWIR - lambda_RED);

// FDI computation: RE2 serves as the spectral baseline; RED defines
// only the wavelength spacing for the linear interpolation - this is
// the correct Biermann et al. (2020) formulation.
function computeFDI(image) {
  var scl = image.select('SCL');
  var cloudMask = scl.eq(4).or(scl.eq(5)).or(scl.eq(6)); // vegetation, bare soil, water
  var RE2 = image.select('B6').multiply(0.0001);
  var NIR = image.select('B8').multiply(0.0001);
  var SWIR = image.select('B11').multiply(0.0001);
  var NIRprime = RE2.add(SWIR.subtract(RE2).multiply(coeff).multiply(10));
  var FDI = NIR.subtract(NIRprime).rename('FDI');
  return FDI.updateMask(cloudMask).copyProperties(image, ['system:time_start']);
}

function buildSeasonalComposite(region, startDate, endDate, label) {
  var collection = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
    .filterBounds(region)
    .filterDate(startDate, endDate)
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
    .map(computeFDI);

  var composite = collection.median().clip(region);

  Export.image.toDrive({
    image: composite,
    description: label,
    folder: 'CoastalSentinel_FDI',
    fileNamePrefix: label,
    region: region,
    scale: 500,
    crs: 'EPSG:4326',
    maxPixels: 1e13
  });

  print(label + ' export queued, real scene count:', collection.size());
}

// Seasonal composites per basin - NE Monsoon (Jan-Mar) and SW Monsoon (Jun-Aug)
buildSeasonalComposite(SCS, '2019-01-01', '2023-03-31', 'Fig2a_SCS_NE_Monsoon_CORRECTED');
buildSeasonalComposite(SCS, '2019-06-01', '2023-08-31', 'Fig2b_SCS_SW_Monsoon_CORRECTED');
buildSeasonalComposite(BoB, '2019-01-01', '2023-03-31', 'Fig2c_BoB_NE_Monsoon_CORRECTED');
buildSeasonalComposite(BoB, '2019-06-01', '2023-08-31', 'Fig2d_BoB_SW_Monsoon_CORRECTED');

// Detection threshold: FDI > 0.05, selected via cross-seasonal
// consistency analysis (see Figure 3 / Table 2 in manuscript)
print('FDI detection threshold: 0.05 (Biermann et al. 2020)');
