from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import sys
import pywavefront
from stl import mesh

angle = 0
model_display_list = None
rotation_speed = 3
model_scale = 0.1
zoom_level = -20

def load_obj_model(filename):
    return pywavefront.Wavefront(filename, collect_faces=True)

# Load STL model
def load_stl_model(filename):
    return mesh.Mesh.from_file(filename)

def create_display_list():
    global model_display_list
    model_display_list = glGenLists(1)
    glNewList(model_display_list, GL_COMPILE)
    
    glBegin(GL_TRIANGLES)
    if model_type == "obj":
        for mesh_obj in model.meshes.values():
            for face in mesh_obj.faces:
                for vertex in face:
                    glVertex3fv(model.vertices[vertex])
    elif model_type == "stl":
        for triangle in model.vectors:
            for vertex in triangle:
                glVertex3fv(vertex)
    glEnd()
    
    glEndList()

def init():
    glEnable(GL_DEPTH_TEST)
    glClearColor(0, 0, 0, 1.0)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, 1, 0.1, 50)
    glMatrixMode(GL_MODELVIEW)
    create_display_list()

def draw_scene():
    global angle
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glTranslatef(0.0, 0.0, zoom_level)
    glScalef(model_scale, model_scale, model_scale)
    glRotatef(angle, 1, 1, 1)
    
    glColor3f(1, 1, 1)  # White model  
    glCallList(model_display_list)  
    
    glutSwapBuffers()
    angle += rotation_speed


def timer(value):
    glutPostRedisplay()
    glutTimerFunc(16, timer, 0)

def keyboard(key, x, y):
    global rotation_speed, model_scale, zoom_level
    key = key.decode("utf-8")
    if key == 'w':
        rotation_speed += 1
    elif key == 's':
        rotation_speed = max(1, rotation_speed - 1)
    elif key == 'a':
        model_scale = max(0.05, model_scale - 0.05)
    elif key == 'd':
        model_scale = min(0.5, model_scale + 0.05)
    elif key == 'z':
        zoom_level += 1
    elif key == 'x':
        zoom_level -= 1

def main():
    global model, model_type
    
    if len(sys.argv) < 3 or sys.argv[1] != '--cad':
        print("Usage: python spinner.py --cad file.obj|file.stl")
        sys.exit(1)

    cad_file = sys.argv[2]
    if cad_file.endswith(".obj"):
        model = load_obj_model(cad_file)
        model_type = "obj"
    elif cad_file.endswith(".stl"):
        model = load_stl_model(cad_file)
        model_type = "stl"
    else:
        print("Unsupported file format! Please use .obj or .stl.")
        sys.exit(1)

    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(500, 500)
    glutCreateWindow(b"Spinner")
    
    init()
    glutDisplayFunc(draw_scene)
    glutTimerFunc(0, timer, 0)
    glutKeyboardFunc(keyboard)  
    glutMainLoop()

if __name__ == "__main__":
    main()
