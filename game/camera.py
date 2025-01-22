import math

class Camera:

    fov = 0
    dir_x = 0
    dir_y = 0
    plane_x = 0
    plane_y = 0

    @staticmethod
    def init():
        Camera.fov = 0.66#1

        Camera.plane_x = 0
        Camera.plane_y = Camera.fov
        print("FOV: " + str(math.degrees(Camera.plane_y)))


    @staticmethod
    def rotate_right(amount: float):
        dir_x, dir_y = Camera.get_dir()
        old_dir_x = dir_x

        dir_x = dir_x * math.cos(-amount) - dir_y * math.sin(-amount)
        dir_y = old_dir_x * math.sin(-amount) + dir_y * math.cos(-amount)

        plane_x, plane_y = Camera.get_plane()
        old_plane_x = plane_x

        plane_x = plane_x * math.cos(-amount) - plane_y * math.sin(-amount)
        plane_y = old_plane_x * math.sin(-amount) + plane_y * math.cos(-amount)

        Camera.dir_x = dir_x
        Camera.dir_y = dir_y
        Camera.plane_x = plane_x
        Camera.plane_y = plane_y

    @staticmethod
    def rotate_left(amount: float):
        dir_x, dir_y = Camera.get_dir()
        old_dir_x = dir_x

        dir_x = dir_x * math.cos(amount) - dir_y * math.sin(amount)
        dir_y = old_dir_x * math.sin(amount) + dir_y * math.cos(amount)

        plane_x, plane_y = Camera.get_plane()
        old_plane_x = plane_x

        plane_x = plane_x * math.cos(amount) - plane_y * math.sin(amount)
        plane_y = old_plane_x * math.sin(amount) + plane_y * math.cos(amount)

        Camera.dir_x = dir_x
        Camera.dir_y = dir_y
        Camera.plane_x = plane_x
        Camera.plane_y = plane_y

    @staticmethod
    # Make the camera look at a point (rotating it)
    def look_at(angle: float):
        # Calculate new direction vectors based on the given angle
        new_dir_x = math.cos(angle)
        new_dir_y = math.sin(angle)
        #new_plane_x = -math.sin(angle)
        # new_plane_y = math.cos(angle)

        # # Update camera direction and plane vectors
        Camera.dir_x = new_dir_x
        Camera.dir_y = new_dir_y
        #Camera.plane_x = new_plane_x
        # Camera.plane_y = new_plane_y

        # Preserves the fov
        new_plane_x = -math.sin(angle) * Camera.fov
        new_plane_y = math.cos(angle) * Camera.fov
        Camera.plane_y = new_plane_y
        Camera.plane_x = new_plane_x

    @staticmethod
    def get_plane():
        return Camera.plane_x, Camera.plane_y
    
    @staticmethod
    def get_dir():
        return Camera.dir_x, Camera.dir_y