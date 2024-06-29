use kiss3d::light::Light;
use kiss3d::window::Window;
use nalgebra::{Point3, Rotation3, Translation3, UnitQuaternion, UnitVector3, Vector3};
use rand::random;

fn main() {
    let c0: f32 = 5f32.sqrt() / 4.;
    let c1: f32 = (5. + 5f32.sqrt()) / 8.;
    let c2: f32 = (5. + 3. * 5f32.sqrt()) / 8.;
    let z: f32 = 0.;

    let vertices: [Vector3<f32>; 32] = [
        [c1, z, c2].into(),
        [c1, z, -c2].into(),
        [-c1, z, c2].into(),
        [-c1, z, -c2].into(),
        [c2, c1, z].into(),
        [c2, -c1, z].into(),
        [-c2, c1, z].into(),
        [-c2, -c1, z].into(),
        [z, c2, c1].into(),
        [z, c2, -c1].into(),
        [z, -c2, c1].into(),
        [z, -c2, -c1].into(),
        [z, c0, c2].into(),
        [z, c0, -c2].into(),
        [z, -c0, c2].into(),
        [z, -c0, -c2].into(),
        [c2, z, c0].into(),
        [c2, z, -c0].into(),
        [-c2, z, c0].into(),
        [-c2, z, -c0].into(),
        [c0, c2, z].into(),
        [c0, -c2, z].into(),
        [-c0, c2, z].into(),
        [-c0, -c2, z].into(),
        [c1, c1, c1].into(),
        [c1, c1, -c1].into(),
        [c1, -c1, c1].into(),
        [c1, -c1, -c1].into(),
        [-c1, c1, c1].into(),
        [-c1, c1, -c1].into(),
        [-c1, -c1, c1].into(),
        [-c1, -c1, -c1].into(),
    ];

    let faces: [[usize; 4]; 30] = [
        [12, 0, 2, 14],
        [14, 0, 10, 26],
        [26, 0, 5, 16],
        [13, 1, 9, 25],
        [25, 1, 4, 17],
        [17, 1, 5, 27],
        [28, 2, 6, 18],
        [18, 2, 7, 30],
        [30, 2, 10, 14],
        [19, 3, 6, 29],
        [29, 3, 9, 13],
        [13, 3, 1, 15],
        [20, 4, 8, 24],
        [24, 4, 0, 16],
        [16, 4, 5, 17],
        [18, 7, 6, 19],
        [19, 7, 3, 31],
        [31, 7, 11, 23],
        [22, 8, 6, 28],
        [28, 8, 2, 12],
        [12, 8, 0, 24],
        [29, 9, 6, 22],
        [22, 9, 8, 20],
        [20, 9, 4, 25],
        [30, 10, 7, 23],
        [23, 10, 11, 21],
        [21, 10, 5, 26],
        [31, 11, 3, 15],
        [15, 11, 1, 27],
        [27, 11, 5, 21],
    ];

    // face_center_vecs.

    let mut window = Window::new("Light Curve Simulator");
    faces.iter().for_each(|face| {
        let mut q = window.add_quad_with_vertices(
            face.iter()
                .map(|vertex_index| Point3::<f32>::from(vertices[*vertex_index]))
                .collect::<Vec<_>>()
                .as_slice(),
            2,
            2,
        );
        q.set_color(random(), random(), random());
    });

    let face_center_vecs = faces
        .iter()
        .map(|face| {
            (vertices[face[0]] + vertices[face[1]] + vertices[face[2]] + vertices[face[3]]) / 4.
        })
        .collect::<Vec<Vector3<f32>>>();

    face_center_vecs.iter().for_each(|center| {
        let mut c = window.add_cone(0.5, 2.);
        c.append_rotation(
            &Rotation3::rotation_between(
                &UnitVector3::new_normalize(-Vector3::y()),
                &UnitVector3::new_normalize(*center),
            )
            .map_or_else(
                || UnitQuaternion::from_axis_angle(&Vector3::x_axis(), std::f32::consts::PI),
                |r| UnitQuaternion::from_rotation_matrix(&r),
            ),
        );
        c.set_points_size(10.0);
        c.set_lines_width(1.0);
        c.set_surface_rendering_activation(false);
        c.append_translation(&Translation3::from(*center));
        c.set_color(1., 0.8, 0.2);
    });

    window.set_light(Light::StickToCamera);

    while window.render() {}
}
