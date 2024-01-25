import numpy as np


def load(file_name):
    vertices = []
    faces = []
    with open(file_name) as f:
        for line in f:
            tokens = line.strip().split(" ")
            if tokens[0] == "v":
                tri = [float(x) for x in tokens[1:4]]
                vertices.append(np.array((*tri, 1.0), dtype=float))
            elif tokens[0] == "f":
                faces.append([int(x.split("/")[0]) - 1 for x in tokens[1:]])
    tris = poly_to_tri(faces, vertices)

    return vertices, tris


def poly_to_tri(faces, vertices):
    new_faces = []
    for f in faces:
        n = len(f)
        if n == 3:
            new_faces.append(f)
        elif n == 4:
            f1 = f[:3]
            f2 = [f[0], f[2], f[3]]
            new_faces.append(f1)
            new_faces.append(f2)
        elif n > 4:
            verts = np.array([vertices[v] for v in f])
            center_vert = np.mean(verts, axis=0)
            vertices.append(center_vert)
            center_index = len(vertices) -1
            for i, v in enumerate(verts):
                new_faces.append(
                    [
                        f[i],
                        f[(i + 1)%n],
                        center_index
                    ]
                )

            # TODO implement
            # define a vertext that is the center,
            # then go around the ring, and connect each two
            # vert indexes to center
            pass
    return new_faces

if __name__ == "__main__":
    verts, faces = load("../assets/porygon/model.obj")
