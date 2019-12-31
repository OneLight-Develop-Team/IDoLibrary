# This code is called when instances of this SOP cook.
geo = hou.pwd().geometry()
prims = geo.prims()
points = geo.points()

# parms
output = 0
maxIter = 10
threshold = 0.001

centroid = sum([point.position() for point in points], hou.Vector3()) * (1.0 / len(points))

# build covariance matrix
val11 = 0;  val12 = 0;  val13 = 0
val21 = 0;  val22 = 0;  val23 = 0
val31 = 0;  val32 = 0;  val33 = 0

for point in points:
    pos = point.position()
    val11 += (pos[0] - centroid[0]) * (pos[0] - centroid[0])
    val12 += (pos[0] - centroid[0]) * (pos[1] - centroid[1])
    val13 += (pos[0] - centroid[0]) * (pos[2] - centroid[2])
    val21 += (pos[1] - centroid[1]) * (pos[0] - centroid[0])
    val22 += (pos[1] - centroid[1]) * (pos[1] - centroid[1])
    val23 += (pos[1] - centroid[1]) * (pos[2] - centroid[2])
    val31 += (pos[2] - centroid[2]) * (pos[0] - centroid[0])
    val32 += (pos[2] - centroid[2]) * (pos[1] - centroid[1])
    val33 += (pos[2] - centroid[2]) * (pos[2] - centroid[2])

mat = hou.Matrix3(((val11, val12, val13), (val21, val22, val23), (val31, val32, val33)))
mat = hou.Matrix4(mat.inverted())

# search for eigenvector with lowest eigenvalue
vec1 = hou.Vector3(1.0, 1.0, 1.0)
vecTemp = vec1 * mat
vec2 = vecTemp * (1.0 / vecTemp.length())
i = 0
while not vec1.isAlmostEqual(vec2) and i < 100:
    vec1 = vec2
    vecTemp = vec1 * mat
    vec2 = vecTemp * (1.0 / vecTemp.length())
    i += 1
minAxis = vec2.normalized()


# build matrix to transform geometry to initial position and orientation
up = hou.Vector3(0.0, 1.0, 0.0)
matUp = hou.hmath.buildTranslate(-centroid)
matUp *= minAxis.matrixToRotateTo(up)
geo.transform(matUp)

# initialize attributes
initRot = 9
angleSum = 0
ratio = 1
i = 0

# adaptively rotate geometry until best orientation for smallest bounding box is found
while i < maxIter and ratio > threshold:
    angle = 0
    angleHold = 0
    angleRotBest = 0
    bboxSize = geo.boundingBox().sizevec()
    vol = bboxSize[0] * bboxSize[1] * bboxSize[2]
    volMin = vol
    volMinHold = vol

    for n in range(10):
        angle += initRot
        matRot = hou.hmath.buildRotateAboutAxis(up, initRot)
        geo.transform(matRot)
        
        bboxSize = geo.boundingBox().sizevec()
        vol = bboxSize[0] * bboxSize[1] * bboxSize[2]
        if vol < volMin:
            volMin = vol
            angleRotBest = angle
    
    # check ratio of vol and vol of previous bounding box
    ratio = abs(volMinHold - volMin)
    volMinHold = volMin
    if ratio == 0.0 and i == 0:
        ratio = 1.0
    
    angleRot = angle - angleRotBest + initRot
    angleSum += angleRotBest - initRot
    matRot = hou.hmath.buildRotateAboutAxis(up, -angleRot)
    geo.transform(matRot) 
    initRot *= 0.2
    i += 1


# bounding box 
bbox = geo.boundingBox()
size = bbox.sizevec()
vol = size[0] * size[1] * size[2]

# build matrix to transform geometry back to oiginal position and orientation
mat = hou.hmath.buildRotateAboutAxis(up, -angleSum) * matUp.inverted()
matAttrib = geo.findGlobalAttrib("mat")
if not matAttrib:
    matAttrib = geo.addAttrib(hou.attribType.Global, "mat", (   0.0, 0.0, 0.0, 0.0,
                                                                0.0, 0.0, 0.0, 0.0,
                                                                0.0, 0.0, 0.0, 0.0,
                                                                0.0, 0.0, 0.0, 0.0))
geo.setGlobalAttribValue(matAttrib, mat.asTuple())






