from pathlib import Path
from ament_index_python import get_package_share_directory

from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    GroupAction
)
from launch.conditions import IfCondition
from launch.launch_description_sources import FrontendLaunchDescriptionSource # Python 실행 파일을 포함시키기 위해 Frontend 사용
from launch.substitutions import LaunchConfiguration

from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue

from srdfdom.srdf import SRDF

def generate_launch_description():
    ld = LaunchDescription()

    package_name = 'astra_controller'
    package_path = Path(get_package_share_directory(package_name))

    ld.add_action(
        DeclareLaunchArgument(
            "rviz_config",
            default_value=str(package_path / "config/default.rviz"),
        )
    )

    # --- 카메라 노드 실행 (변경 없음) ---
    # 헤드 카메라
    ld.add_action(
        Node(
            package='usb_cam', executable='usb_cam_node_exe',
            namespace='cam_head',
            parameters=[{
                'video_device': '/dev/video_head',
                'pixel_format': 'mjpeg2rgb',
                'image_width': 640,
                'image_height': 360,
                'framerate': 30.0,
            }],
            output={'both': 'log'},
        )
    )
    # 왼쪽 손목 카메라
    ld.add_action(
        Node(
            package='usb_cam', executable='usb_cam_node_exe',
            namespace='left/cam_wrist',
            parameters=[{
                'video_device': '/dev/video_wrist_left',
                'pixel_format': 'mjpeg2rgb',
                'image_width': 640,
                'image_height': 360,
                'framerate': 30.0,
            }],
            output={'both': 'log'},
        )
    )
    # 오른쪽 손목 카메라
    ld.add_action(
        Node(
            package='usb_cam', executable='usb_cam_node_exe',
            namespace='right/cam_wrist',
            parameters=[{
                'video_device': '/dev/video_wrist_right',
                'pixel_format': 'mjpeg2rgb',
                'image_width': 640,
                'image_height': 360,
                'framerate': 30.0,
            }],
            output={'both': 'log'},
        )
    )

    # --- <<수정 시작>> ---
    # --- 실제 로봇 팔 제어 노드 주석 처리 ---
    # ld.add_action(
    #     Node(
    #         package=package_name,
    #         executable="lift_node",
    #         namespace='left/lift',
    #         parameters=[{
    #             'device': '/dev/tty_puppet_lift_left',
    #             'joint_names': [ "joint_l1", ],
    #         }],
    #         remappings=[
    #             ('joint_states', '/joint_states'),
    #         ],
    #         output='screen',
    #         emulate_tty=True,
    #     )
    # )
    # ld.add_action(
    #     Node(
    #         package=package_name,
    #         executable="arm_node",
    #         namespace='left/arm',
    #         parameters=[{
    #             'device': '/dev/tty_puppet_left',
    #             'joint_names': [ "joint_l2", "joint_l3", "joint_l4", "joint_l5", "joint_l6", ],
    #             'gripper_joint_names': [ "joint_l7l", "joint_l7r", ],
    #         }],
    #         remappings=[
    #             ('joint_states', '/joint_states'),
    #             ('gripper_joint_states', '/joint_states'),
    #         ],
    #         output='screen',
    #         emulate_tty=True,
    #     )
    # )
    # ld.add_action(
    #     Node(
    #         package=package_name,
    #         executable="lift_node",
    #         namespace='right/lift',
    #         parameters=[{
    #             'device': '/dev/tty_puppet_lift_right',
    #             'joint_names': [ "joint_r1", ],
    #         }],
    #         remappings=[
    #             ('joint_states', '/joint_states'),
    #         ],
    #         output='screen',
    #         emulate_tty=True,
    #     )
    # )
    # ld.add_action(
    #     Node(
    #         package=package_name,
    #         executable="arm_node",
    #         namespace='right/arm',
    #         parameters=[{
    #             'device': '/dev/tty_puppet_right',
    #             'joint_names': [ "joint_r2", "joint_r3", "joint_r4", "joint_r5", "joint_r6", ],
    #             'gripper_joint_names': [ "joint_r7l", "joint_r7r", ],
    #         }],
    #         remappings=[
    #             ('joint_states', '/joint_states'),
    #             ('gripper_joint_states', '/joint_states'),
    #         ],
    #         output='screen',
    #         emulate_tty=True,
    #     )
    # )

    # --- 시뮬레이션 로봇 팔 (dry_run_node) 실행 ---
    # 왼쪽 팔 시뮬레이션
    ld.add_action(
        Node(
            package=package_name,
            executable="dry_run_node", # dry_run_node.py 실행
            namespace='left', # 왼쪽 팔 네임스페이스
            parameters=[{
                'actively_send_joint_state': True, # 주기적으로 관절 상태 발행
                'joint_names': [ "joint_l1", "joint_l2", "joint_l3", "joint_l4", "joint_l5", "joint_l6", "joint_l7r", "joint_l7l" ], # 왼쪽 팔 관절 이름
            }],
            remappings=[
                ('joint_states', '/joint_states'), # '/left/joint_states'를 '/joint_states'로 통합
            ],
            # dry_run_node.py는 Python 스크립트이므로 emulate_tty=True가 필요할 수 있음
            # output='screen',
            # emulate_tty=True,
        )
    )
    # 오른쪽 팔 시뮬레이션
    ld.add_action(
        Node(
            package=package_name,
            executable="dry_run_node", # dry_run_node.py 실행
            namespace='right', # 오른쪽 팔 네임스페이스
            parameters=[{
                'actively_send_joint_state': True,
                'joint_names': [ "joint_r1", "joint_r2", "joint_r3", "joint_r4", "joint_r5", "joint_r6", "joint_r7r", "joint_r7l" ], # 오른쪽 팔 관절 이름
            }],
            remappings=[
                ('joint_states', '/joint_states'), # '/right/joint_states'를 '/joint_states'로 통합
            ],
            # output='screen',
            # emulate_tty=True,
        )
    )
    # --- <<수정 끝>> ---

    # --- 역기구학(IK) 계산 노드 실행 (변경 없음) ---
    ld.add_action(
        Node(
            package=package_name,
            executable="ik_node",
            namespace='left',
            parameters=[{
                'eef_link_name': 'link_lee_teleop',
                'joint_names': ['joint_l1', 'joint_l2', 'joint_l3', 'joint_l4', 'joint_l5', 'joint_l6'],
            }],
        )
    )
    ld.add_action(
        Node(
            package=package_name,
            executable="ik_node",
            namespace='right',
            parameters=[{
                'eef_link_name': 'link_ree_teleop',
                'joint_names': ['joint_r1', 'joint_r2', 'joint_r3', 'joint_r4', 'joint_r5', 'joint_r6'],
            }],
        )
    )

    # --- 로봇 베이스 제어 노드 실행 (변경 없음, 필요시 dry_run_node와 유사하게 시뮬레이션 노드로 대체 가능) ---
    ld.add_action(
        Node(
            package=package_name,
            executable="base_node",
            parameters=[{
                'device': 'can0',
            }],
        )
    )

    # --- 로봇 헤드 제어 노드 실행 (변경 없음, 필요시 dry_run_node와 유사하게 시뮬레이션 노드로 대체 가능) ---
    ld.add_action(
        Node(
            package=package_name,
            executable="head_node",
            namespace='head',
            parameters=[{
                'device': '/dev/tty_head',
            }],
            remappings=[
                ('joint_states', '/joint_states'),
            ],
            output='screen',
            emulate_tty=True,
        )
    )

    # --- 웹 기반 원격 조작 노드 실행 (변경 없음) ---
    ld.add_action(
        Node(
            package=package_name,
            executable="teleop_web_node",
            output='screen',
            emulate_tty=True,
        )
    )

    # --- 로봇 모델 시각화 관련 실행 파일 포함 (변경 없음) ---
    ld.add_action(
        IncludeLaunchDescription(
            FrontendLaunchDescriptionSource([
                str(Path(get_package_share_directory('astra_description'))
                    / 'launch' / 'publish_model.launch'),
            ]),
        )
    )

    # --- RViz2 실행 (주석 해제 권장) ---
    # 시뮬레이션 결과를 RViz에서 확인하기 위해 주석 해제
    ld.add_action(
        Node(
            package="rviz2",
            executable="rviz2",
            respawn=False,
            arguments=["-d", LaunchConfiguration("rviz_config")],
            output={'both': 'log'},
        )
    )

    # # --- PlotJuggler 실행 (선택 사항) ---
    # ld.add_action(
    #     Node(
    #         package="plotjuggler",
    #         executable="plotjuggler",
    #         respawn=False,
    #     )
    # )

    return ld