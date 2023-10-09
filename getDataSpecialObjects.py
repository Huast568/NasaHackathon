from roboflow import Roboflow
def getDataSpecialObjects(pathToImage):
    rf = Roboflow(api_key="CImlsMQkacpKzTkkdHaR")

    project_nebula = rf.workspace().project("nebula-1nsta")
    model_nebula = project_nebula.version(1).model
    project_bodies = rf.workspace().project("space-image-detection")
    model_bodies = project_bodies.version(1).model
    project_galaxy = rf.workspace().project("galaxy_detection_wcc_project")
    model_galaxy = project_galaxy.version(4).model
    img_file = pathToImage
    m1 = model_nebula.predict(img_file, confidence=40, overlap=30).json()
    m2 = model_bodies.predict(img_file, confidence=40, overlap=30).json()
    m3 = model_galaxy.predict(img_file, confidence=40, overlap=30).json()

    p1 = m1['predictions']
    p2 = m2['predictions']
    p3 = m3['predictions']

    special_obj = []
# (class, x, y)

    a = 'y'
    b = 'width'

    for i in p1:
        special_obj.append((i[a], i[a] + i[b]))

    for i in p2:
        special_obj.append((i[a], i[a] + i[b]))

    for i in p3:
        special_obj.append((i[a], i[a] + i[b]))

    return special_obj
