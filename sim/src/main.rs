use std::net::UdpSocket;

use artnet_protocol::ArtCommand;
use kiss3d::{camera::ArcBall, light::Light, window::Window};
use nalgebra::{Point3, Translation3, UnitQuaternion, Vector3};
use rand::random;

fn main() {
    let socket = setup_socket();
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

    let quaternion_to_rotate_5_pyramid_to_top =
        UnitQuaternion::rotation_between(&vertices[8], &Vector3::y()).unwrap();

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
        q.append_rotation(&quaternion_to_rotate_5_pyramid_to_top);
        q.set_color(random(), random(), random());
    });

    let face_center_vectors = faces
        .iter()
        .map(|face| {
            // Average the vertex vectors to create the vector to the center of the face
            (vertices[face[0]] + vertices[face[1]] + vertices[face[2]] + vertices[face[3]]) / 4.
        })
        .collect::<Vec<Vector3<f32>>>();

    face_center_vectors.iter().for_each(|center| {
        let mut c = window.add_cone(0.5, 2.);
        c.append_rotation(
            &UnitQuaternion::rotation_between(&(-Vector3::y()), center).unwrap_or_else(|| {
                UnitQuaternion::from_axis_angle(&Vector3::x_axis(), std::f32::consts::PI)
            }),
        );
        c.set_points_size(10.0);
        c.set_lines_width(1.0);
        c.set_surface_rendering_activation(false);
        c.append_translation(&Translation3::from((*center) * 1.5));
        c.append_rotation(&quaternion_to_rotate_5_pyramid_to_top);
        c.set_color(1., 0.8, 0.2);
    });

    window.set_light(Light::StickToCamera);

    let mut arc_ball_camera = ArcBall::new(Point3::new(6.0f32, 6., 6.), Point3::origin());

    while !window.should_close() {
        window.render_with_camera(&mut arc_ball_camera);
        receive_artnet(&socket);
    }
}

fn setup_socket() -> UdpSocket {
    let udp_socket = match UdpSocket::bind("0.0.0.0:6454") {
        Ok(socket) => socket,
        Err(e) => {
            println!("Error binding: {:?}", e);
            panic!();
        }
    };
    udp_socket.set_nonblocking(true).unwrap();
    udp_socket
}

fn receive_artnet(socket: &UdpSocket) {
    let mut response_buf = [0u8; 65507];
    let Ok((response_length, player_address)) = socket.recv_from(&mut response_buf) else {
        // Received nothing
        return;
    };

    match ArtCommand::from_buffer(&response_buf[..response_length]) {
        Err(e) => {
            println!(
                "Received bytes that aren't a valid artnet command from {:?}: {:?}",
                player_address, e
            );
        }
        Ok(ArtCommand::Output(output)) => {
            let data = output.data.as_ref();
            println!("{:?}", data);
            // let numNozzlesReceived = faces.len().min(numBytesReceived / 2);
            // data.chunks(2).take(numNozzlesReceived * 2).for_each(|byte|{

            //     // for (int nozzleIndex = 0; nozzleIndex < numNozzlesReceived; nozzleIndex++)
            //     // {
            //     //   int valveDataStartIndex = nozzleIndex * 2;
            //     //   uint8_t solenoidByte = data[valveDataStartIndex];
            //     //   uint8_t servoByte = data[valveDataStartIndex + 1];
            //     //   float servoByteFloat = (float)servoByte;
            //     //   setSolenoidState(nozzleIndex, solenoidByte > 0);
            //     //   setValveState(nozzleIndex, servoByteFloat / 255.0);
            //     // }
            // });
        }
        _ => {
            // E.g. this will happen when the device receives its own poll message that was broadcast on the network.
            println!(
                "Received artnet that is not PollReply from {:?}",
                player_address
            );
        }
    }
}
