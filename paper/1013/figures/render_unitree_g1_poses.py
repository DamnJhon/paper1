"""Render three hand-posed illustrations from the Unitree G1 29-DoF MJCF.

Run with MUJOCO_GL=egl and pass the path to g1_29dof_rev_1_0.xml.
The joint configurations illustrate stages and are not simulation samples.
"""

import argparse
from pathlib import Path

import mujoco
import numpy as np
from PIL import Image


POSES = {
    # hip pitch, knee, ankle pitch, shoulder pitch, elbow, waist pitch
    "takeoff": (-0.17, 0.34, 0.20, -1.05, 0.22, 0.19),
    "flight": (-1.04, 1.66, -0.24, -0.86, 0.50, 0.12),
    "landing": (-0.81, 1.42, -0.61, -0.80, 0.38, 0.28),
}
LIMB_JOINTS = ("hip_pitch", "knee", "ankle_pitch", "shoulder_pitch", "elbow")


def render(model_path):
    model = mujoco.MjModel.from_xml_path(str(model_path))
    model.vis.headlight.ambient[:] = 0.34
    data = mujoco.MjData(model)
    camera = mujoco.MjvCamera()
    camera.azimuth = 112
    camera.elevation = -7
    camera.distance = 2.38
    camera.lookat[:] = (0, 0, 0.73)
    options = mujoco.MjvOption()
    options.geomgroup[:] = 0
    options.geomgroup[1] = 1
    options.sitegroup[:] = 0
    out = Path(__file__).resolve().parent / "overview" / "g1_poses"
    out.mkdir(exist_ok=True)
    with mujoco.Renderer(model, height=480, width=600) as renderer:
        for phase, values in POSES.items():
            mujoco.mj_resetData(model, data)
            for side, sign in (("left", 1), ("right", -1)):
                for joint, value in zip(LIMB_JOINTS, values):
                    data.joint(f"{side}_{joint}_joint").qpos[0] = value
                data.joint(f"{side}_shoulder_roll_joint").qpos[0] = sign * 0.13
            data.joint("waist_pitch_joint").qpos[0] = values[-1]
            mujoco.mj_forward(model, data)
            renderer.disable_segmentation_rendering()
            renderer.update_scene(data, camera=camera, scene_option=options)
            rgb = renderer.render().copy()
            renderer.enable_segmentation_rendering()
            renderer.update_scene(data, camera=camera, scene_option=options)
            visible = renderer.render()[:, :, 0] >= 0
            rgba = np.dstack((rgb, visible.astype(np.uint8) * 255))
            frame = Image.fromarray(rgba)
            bounds = frame.getbbox()
            if (bounds is None or 0 in bounds[:2]
                    or bounds[2] == frame.width or bounds[3] == frame.height):
                raise RuntimeError(f"The {phase} pose is missing or clipped")
            frame.crop(bounds).save(out / f"{phase}.png")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("model", type=Path)
    render(parser.parse_args().model)
