import os

def create_test_fbx(filepath):
    # Two cubes stacked
    # Cube 1: base (-50..50, -50..50, 0..50) with mat 0
    # Cube 2: top (-30..30, -30..30, 50..100) with mat 1
    # Vertices: 16
    v = [
        # Cube 1 (0..7)
        -50, -50, 0,   50, -50, 0,   50, 50, 0,   -50, 50, 0,
        -50, -50, 50,  50, -50, 50,  50, 50, 50,  -50, 50, 50,
        # Cube 2 (8..15)
        -30, -30, 50,  30, -30, 50,  30, 30, 50,  -30, 30, 50,
        -30, -30, 100, 30, -30, 100, 30, 30, 100, -30, 30, 100
    ]
    # Faces: quads (or triangles). In FBX, quad is v0, v1, v2, -(v3+1).
    def quad(a, b, c, d):
        return [a, b, c, -(d + 1)]

    faces = [
        # Cube 1 faces (6 quads) -> 0..5
        quad(0, 3, 2, 1), # bottom
        quad(4, 5, 6, 7), # top
        quad(0, 1, 5, 4), # front
        quad(1, 2, 6, 5), # right
        quad(2, 3, 7, 6), # back
        quad(3, 0, 4, 7), # left
        # Cube 2 faces (6 quads) -> 6..11
        quad(8, 11, 10, 9),
        quad(12, 13, 14, 15),
        quad(8, 9, 13, 12),
        quad(9, 10, 14, 13),
        quad(10, 11, 15, 14),
        quad(11, 8, 12, 15),
    ]

    pvi = []
    for f in faces:
        pvi.extend(f)

    # Materials per face: 6 faces mat 0, 6 faces mat 1
    mats = [0]*6 + [1]*6

    v_str = ",".join(f"{x:.4f}" for x in v)
    pvi_str = ",".join(str(x) for x in pvi)
    mats_str = ",".join(str(m) for m in mats)

    fbx_text = f"""; FBX 7.3.0 project file
FBXHeaderExtension:  {{
	FBXHeaderVersion: 1003
	FBXVersion: 7300
}}
GlobalSettings:  {{
	Version: 1000
	Properties70:  {{
		P: "UpAxis", "int", "Integer", "",2
		P: "UpAxisSign", "int", "Integer", "",1
		P: "FrontAxis", "int", "Integer", "",1
		P: "FrontAxisSign", "int", "Integer", "",-1
		P: "CoordAxis", "int", "Integer", "",0
		P: "CoordAxisSign", "int", "Integer", "",1
		P: "UnitScaleFactor", "double", "Number", "",1.0
	}}
}}
Definitions:  {{
	Version: 100
	Count: 4
	ObjectType: "Model" {{
		Count: 1
	}}
	ObjectType: "Geometry" {{
		Count: 1
	}}
	ObjectType: "Material" {{
		Count: 2
	}}
}}
Objects:  {{
	Model: 10001, "Model::TestMesh", "Mesh" {{
		Version: 232
		Properties70:  {{
			P: "InheritType", "enum", "", "",1
		}}
		Shading: T
		Culling: "CullingOff"
	}}
	Geometry: 20001, "Geometry::", "Mesh" {{
		Vertices: *{len(v)} {{
			a: {v_str}
		}}
		PolygonVertexIndex: *{len(pvi)} {{
			a: {pvi_str}
		}}
		GeometryVersion: 124
		LayerElementMaterial: 0 {{
			Version: 101
			Name: ""
			MappingInformationType: "ByPolygon"
			ReferenceInformationType: "IndexToDirect"
			Materials: *{len(mats)} {{
				a: {mats_str}
			}}
		}}
		Layer: 0 {{
			Version: 100
			LayerElement:  {{
				Type: "LayerElementMaterial"
				TypedIndex: 0
			}}
		}}
	}}
	Material: 30001, "Material::MatBase", "" {{
		Version: 102
		ShadingModel: "phong"
	}}
	Material: 30002, "Material::MatTop", "" {{
		Version: 102
		ShadingModel: "phong"
	}}
}}
Connections:  {{
	C: "OO",10001,0
	C: "OO",20001,10001
	C: "OO",30001,10001
	C: "OO",30002,10001
}}
"""
    with open(filepath, "w") as f:
        f.write(fbx_text)

create_test_fbx(r"D:\Game\FishGame\Saved\DownloadedAssets\test_generated.fbx")
print("Wrote test FBX!")
