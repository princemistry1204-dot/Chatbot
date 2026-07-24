def vehicle_labels():
    # 7 Vehicle classes corresponding to the trained model output
    CLASS_NAMES = [
        'Auto Rickshaws', 'Cars', 'Bikes', 'Motorcycles', 'Planes',
        'Ships', 'Trains',
    ]
    return CLASS_NAMES


def vehicle_label():
    return vehicle_labels()

