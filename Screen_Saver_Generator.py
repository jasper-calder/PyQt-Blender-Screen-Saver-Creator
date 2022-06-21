from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, 
    QSlider, QVBoxLayout,
    QWidget, QLabel,
    QPushButton, QRadioButton,
    QComboBox, QHBoxLayout,
    QColorDialog)
import PyQt5.QtWidgets
import random
import bpy

class BlockPattern():

    def __init__(self):
        
        #Block vars
        self.spacing = 0.4
        self.TotalBlockWidth = 20
        self.TotalBlockHeight = 20
        self.BlockWidth = 1
        self.BlockHeight = 3
        self.Randomness = 2
        self.glow = 3
    

        #Colour vars
        self.main_rgba = (255,0,0,255)
        self.side_rgba = (255, 255, 255, 255)
        self.roughness = 1
        self.light_power = 2400

        #Camera vars
        self.CameraHeight = 60
        self.SetNewScene()
        
        #function vars
        self.function = "Random"
        
    
    def SetNewScene(self):
        #Switch to new scene
        new_scene = bpy.data.scenes.new('Wallpaper')
        bpy.context.window.scene = new_scene
        
        
        #Add camera
        bpy.ops.object.camera_add(enter_editmode=False, align='VIEW', location=(0, 0, self.CameraHeight), rotation=(0, 0, 0), scale=(1, 1, 1))
        bpy.context.scene.camera = bpy.context.scene.objects[0]
        print(bpy.context.scene.camera)
        
        #Add Light
        self.AddLight(name="key_light", energy=self.light_power, size=50, location=(0,0, 50), rotation=(0,0,0), type="AREA")
        
        
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                area.spaces[0].region_3d.view_perspective = 'CAMERA'
                break
    
    def selectPattern(self):
        bpy.ops.object.select_all(action="SELECT")

    def deletePattern(self):
        bpy.ops.object.delete()
        
        

    def CreatePattern(self):
        
        main_material = self.CreateMaterial(self.main_rgba, self.roughness, True)
        side_material = self.CreateMaterial(self.side_rgba, self.roughness, False)
        for x in range(int(-1*self.TotalBlockWidth/2), int((self.TotalBlockWidth/2) + 1)):
            for y in range(int(-1*self.TotalBlockHeight/2), int((self.TotalBlockHeight/2) + 1)):
                input_x = x * (2*self.BlockWidth + self.spacing)
                input_y = y * (2*self.BlockWidth + self.spacing)
                location = (input_x, input_y, self.z_function(input_x, input_y, self.function))
                bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', location=location, scale=(self.BlockWidth, self.BlockWidth, self.BlockHeight))
                if random.random() > 0.1:
                    bpy.context.object.active_material = main_material
                else:
                    bpy.context.object.active_material = side_material
                
    def z_function(self, x, y, name):
        
        functions = {
            "Random": random.random() * self.Randomness,
            "Bowl": (x/5)**2 + (y/5)**2,
            "idk":  ((y/7)**3)*((x/7)**3)
        }
        
        return functions[name]
    
    
    def CreateMaterial(self, rgba, roughness, main):
        material_basic = bpy.data.materials.new("Block_Material")
        material_basic.use_nodes = True
        principled_node = material_basic.node_tree.nodes.get("Principled BSDF")
        link = material_basic.node_tree.nodes.new
        if main:
            principled_node.inputs[0].default_value = rgba
            principled_node.inputs[9].default_value = roughness
        else:
            principled_node.inputs[19].default_value = (self.side_rgba[0]/255, self.side_rgba[1]/255, self.side_rgba[2]/255, self.side_rgba[3]/255)
            principled_node.inputs[20].default_value = self.glow
            print(self.side_rgba[0]/255, self.side_rgba[1]/255, self.side_rgba[2]/255, self.side_rgba[3]/255)
        return material_basic
    
    def AddLight(self, **kwargs):
        area_light_data = bpy.data.lights.new(name=kwargs["name"], type=kwargs["type"])
        area_light_data.energy = kwargs["energy"]
        if kwargs["type"] == "AREA":
            area_light_data.size = kwargs["size"]
        area_light_object = bpy.data.objects.new(name=kwargs["name"], object_data=area_light_data)
        bpy.context.collection.objects.link(area_light_object)
        area_light_object.location = kwargs["location"]
        area_light_object.rotation_euler = kwargs["rotation"]




class MainWindow(QMainWindow):

    
    def __init__(self, parent=None, *args, **kwargs):
        super(MainWindow, self).__init__(parent=parent)
        self.setWindowTitle("My App")
        self.setFixedSize(QSize(800,900))
        self.initUI()
        self.pattern = BlockPattern()
        self.pattern.CreatePattern()

        self.show()

    def initUI(self):


        sliders = ["Cube Spacing", "Cube Glow Strength"]
        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        
        # Radio Buttons Default Patterns
        #https://www.benjoffe.com/code/tools/functions3d/examples

        label = QLabel("Select cube pattern")
        label.setAlignment(Qt.AlignCenter | Qt.AlignCenter)
        layout.addWidget(label)

        radio_buttons = ["Random", "Bowl", "Torus", "Bumps", "Intersecting Fences"]
    
        radioButtonLayout = QHBoxLayout()

        for button in radio_buttons:
            radiobutton = QRadioButton(button)
            radiobutton.function = button
            if button == "Random":
                radiobutton.setChecked(True)
            radiobutton.clicked.connect(self.setFunction)
            radioButtonLayout.addWidget(radiobutton)
        
        widget = QWidget()
        widget.setLayout(radioButtonLayout)
        widget.setFixedHeight(50)
        layout.addWidget(widget)

        # Cube properties
        label = QLabel("Adjust Cube Properties")
        label.setAlignment(Qt.AlignCenter | Qt.AlignCenter)
        layout.addWidget(label)

        sliders = ["Cube Spacing", "Cube Height", "Cube Glow Strength", "Cube Shininess"]

        sliderLayout = QHBoxLayout()

        for slider in sliders:
            sliderLayout.addWidget(self.addSlider(slider))

        widget = QWidget()
        widget.setLayout(sliderLayout)

        layout.addWidget(widget)

        

        #Main Colours Dialog
        button = QPushButton("Pick a main colour")
        button.main = True
        button.clicked.connect(self.openColourWidget)
        layout.addWidget(button)

        #Side Colours Dialog
        button = QPushButton("Pick a side colour")
        button.main = False
        button.clicked.connect(self.openColourWidget)
        layout.addWidget(button)

        # Select Button
        button = QPushButton("Select All Cubes")
        button.clicked.connect(self.selectCubes)
        layout.addWidget(button)


        #Apply Delete Button
        button = QPushButton("Delete All Cubes")
        button.clicked.connect(self.deleteCubes)
        layout.addWidget(button)

        #Apply new pattern
        button = QPushButton("Apply new pattern")
        button.clicked.connect(self.applyNewPattern)
        layout.addWidget(button)


        #  Center the layout

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)


    #   Slots
    def selectCubes(self):
        self.pattern.selectPattern()
    

    def deleteCubes(self):
        print("deleting pattern")
        self.pattern.deletePattern()
    
    def applyNewPattern(self):
        self.pattern.CreatePattern()

    def openColourWidget(self):
        color = QColorDialog.getColor()
        button = self.sender()
        if button.main:
            print("Main", color.getRgb())
        else:
            print("Side", color.getRgb())


    def setFunction(self):
        radioButton = self.sender()
        self.pattern.function = radioButton.function


    def sliderValueChanged(self, i):
        slider = self.sender()
        if slider.property == "Cube Spacing":
            self.pattern.spacing = i
        elif slider.property == "Cube Height":
            self.pattern.BlockHeight = i
        elif slider.property == "Cube Glow Strength":
            self.pattern.glow = i


    #Helper function for adding sliders

    def addSlider(self, name):

        layout = QVBoxLayout()
        

        label = QLabel()
        label.setText(name)
        label.setAlignment(Qt.AlignCenter | Qt.AlignCenter)
        label.setFixedHeight(50)
        label.setStyleSheet("border: 2px solid black;")
        layout.addWidget(label)


        sliderWidget = QSlider(Qt.Vertical)
        sliderWidget.property = name
        sliderWidget.setRange(0,10)
        sliderWidget.setSingleStep(1)
        sliderWidget.valueChanged.connect(self.sliderValueChanged)
        layout.addWidget(sliderWidget, Qt.AlignCenter | Qt.AlignCenter)




        widget = QWidget()
        widget.setLayout(layout)

        return widget



