import bpy
import sys
import os
import traceback

def optimize_mesh(input_path: str, output_path: str):
    try:
        print(f"[*] BLENDER SCRIPT STARTING...")
        
        # 1. Clear the default Blender scene
        bpy.ops.wm.read_factory_settings(use_empty=True)

        # 2. Import the raw AI-generated .glb file
        print(f"[*] Loading raw mesh from: {input_path}")
        bpy.ops.import_scene.gltf(filepath=input_path)

        # 3. Select all imported objects
        bpy.ops.object.select_all(action='SELECT')
        
        if not bpy.context.selected_objects:
            print("[!] Error: No objects found in the imported file.")
            sys.exit(1)

        # 4. Math: Center and Scale
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
        for obj in bpy.context.selected_objects:
            obj.location = (0, 0, 0)
        
        bpy.context.view_layer.update() 
        
        max_dimension = max(bpy.context.selected_objects[0].dimensions)
        if max_dimension > 0:
            scale_factor = 1.0 / max_dimension
            bpy.context.selected_objects[0].scale = (scale_factor, scale_factor, scale_factor)

        # Apply the scale and location permanently
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

        # 5. Export using Draco Compression for WebGL
        print(f"[*] Exporting optimized Draco mesh to: {output_path}")
        bpy.ops.export_scene.gltf(
            filepath=output_path,
            export_format='GLB',
            export_draco_mesh_compression_enable=True, # Web Optimizer
            export_draco_mesh_compression_level=6
        )
        print("[*] BLENDER SCRIPT FINISHED SUCCESSFULLY.")
        
    except Exception as e:
        # If Blender crashes, print the exact Python stack trace!
        print("\n[!] BLENDER PYTHON SCRIPT CRASHED:")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
        if len(argv) >= 2:
            optimize_mesh(argv[0], argv[1])
        else:
            print("Usage: blender -b -P optimize.py -- <input> <output>")
    else:
        print("No arguments provided.")