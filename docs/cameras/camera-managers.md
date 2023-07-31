# Camera Managers

A camera manager facilitates all operations with cameras inside Rust.

Creation:

```python
# Get the camera manager from the socket:
camera_manager = await socket.get_camera_manager("drone")
# The parameter is the camera ID
```

**Only one Camera Manager can exist at once**. Once a new one is created the old one will go stale.

## Re Subscribing

Subscriptions only last around 15 seconds. After this, you must resubscribe by doing:

```python
if time.time() - camera_manager.time_since_last_subscribe > 10:
    await camera_manager.resubscribe()
```

## Getting Frames

Camera frames can be fetched for the camera using the following:

```python
camera_manager = await socket.get_camera_manager("drone")
image = await camera_manager.get_frame() # PIL Image
```

This returns a `PIL` Image that can be saved or displayed. When the Camera Manager is first created there is no camera frame available. Use: `camera_manager.has_frame_data()` to check for this.

## Controlling Drones and Cameras

There are many possible movement options that can be sent via the following code:

```python
# Check that it is possible to zoom the camera in and out
if camera_manager.can_move(CameraMovementOptions.FIRE) and \
        camera_manager.can_move(CameraMovementOptions.MOUSE):
    # Send a MovementControl action to the camera
    await camera_manager.send_actions([MovementControls.FIRE_PRIMARY])
    # You can also send just mouse movement or both at the same time:
    await camera_manager.send_mouse_movement(Vector(1, 1))
    await camera_manager.send_combined_movement(
        [MovementControls.FIRE_PRIMARY], Vector(1, 1))

    await asyncio.sleep(1)
    # You must clear the movement after you are done
    # as otherwise the mouse will continue to move and the server
    # Will consider the mouse still clicked down
    await camera_manager.clear_movement()
```
