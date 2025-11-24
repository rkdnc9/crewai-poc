# Test Data for CrewAI Wall Panel QC

This directory contains test IFC files for the Wall Panel Quality Control system.

## Quick Start - Generate Sample File

Run the sample generator to create a test IFC file immediately:

```bash
python create_sample_ifc.py
```

This will create `test_data/sample_wall.ifc` with:
- 2 wall panels (one with intentional violations)
- 1 door opening
- 1 HVAC duct

## Real-World Test Data Sources

For testing with real building models, you can download IFC files from these public sources:

### 1. BuildingNet Dataset
- **URL**: https://github.com/buildingnet/buildingnet_dataset
- **Description**: 50,000+ annotated IFC building exteriors
- **License**: CC-BY
- **Format**: IFC
- **Best for**: Large-scale testing with diverse building types

### 2. BIMserver.org Test Files
- **URL**: https://github.com/opensourceBIM/TestFiles
- **Description**: Collection of IFC test files from various sources
- **License**: Mixed (check individual files)
- **Format**: IFC (various versions)
- **Best for**: Testing IFC compatibility

### 3. IfcOpenShell Sample Files
- **URL**: https://github.com/IfcOpenShell/IfcOpenShell/tree/master/test/input
- **Description**: Test files used by IfcOpenShell project
- **License**: LGPL
- **Format**: IFC
- **Best for**: Basic IFC structure testing

### 4. GrabCAD Construction Models
- **URL**: https://grabcad.com/library/tag/construction
- **Description**: User-contributed CAD models (may need conversion to IFC)
- **Format**: STEP, SOLIDWORKS (requires conversion)
- **Best for**: Detailed wall panel models

## Converting Other Formats to IFC

If you have models in other formats, you can convert them to IFC:

### Using FreeCAD
1. Open the model in FreeCAD
2. Select all objects
3. File → Export → Select "Industry Foundation Classes (*.ifc)"

### Using Blender with BlenderBIM
1. Install BlenderBIM add-on
2. Import your model
3. Export as IFC

### Using Online Converters
- https://www.ifcconverter.com/
- https://products.aspose.app/cad/conversion/step-to-ifc

## File Organization

Organize your test files like this:

```
test_data/
├── README.md (this file)
├── sample_wall.ifc (generated sample)
├── buildingnet/
│   └── (downloaded IFC files)
├── real_projects/
│   └── (your actual project files)
└── converted/
    └── (files converted from other formats)
```

## Testing Workflow

1. Start with the generated sample:
   ```bash
   python main.py --ifc test_data/sample_wall.ifc
   ```

2. Test with real IFC files:
   ```bash
   python main.py --ifc test_data/buildingnet/model_001.ifc
   ```

3. Compare results across different models to validate agent behavior

## Notes

- IFC files can be very large (10MB+). Git LFS is recommended for version control.
- Not all IFC files contain wall panel details - focus on architectural models.
- The POC is optimized for residential/commercial wood-frame or CFS wall panels.
