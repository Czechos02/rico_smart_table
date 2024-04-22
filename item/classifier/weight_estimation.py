import tensorflow as tf

from keras.models import Sequential
from keras.layers import Conv2D, Flatten, Dense, BatchNormalization, ReLU, AveragePooling2D
from keras.optimizers import Adam

HYPERBOLE_A = 35108.0
HYPERBOLE_X0 = 0.0
HYPERBOLE_Y = 0.42
DIVIDER_RESISTANCE = 470
WEIGHT_MULTIPLIER = 2.5740


def estimate_weight(raw_calibrated_image, max_value=4095):
    weight = 0

    for row in raw_calibrated_image:
        for tile in row:
            # Have to be rounded because otherwise have calculation errors with small weight
            normalized_pressure = round(tile * (4095 / max_value), 1)
            try:
                if normalized_pressure >= 4095.0:
                    continue
                resistance = (DIVIDER_RESISTANCE * normalized_pressure) / (4095.0 - normalized_pressure)
                weight += (HYPERBOLE_X0 + (HYPERBOLE_A / (resistance - HYPERBOLE_Y)))
            except ZeroDivisionError:
                continue

    if weight <= 0.0:
        return 0.0

    weight = weight * WEIGHT_MULTIPLIER
    return weight


def estimate_weight_with_model(model, images):
    weight = model.predict(images, verbose=0)
    return weight


def mean_absolute_percentage_square_error(y_true, y_pred):
    y_true = tf.cast(y_true, tf.float32)
    loss = tf.reduce_mean(tf.square(100 * (y_true - y_pred) / y_true))
    return loss


def get_default_weight_estimation_model():
    model = Sequential()

    model.add(Conv2D(16, (3, 3), input_shape=(16, 16, 1), padding="same", strides=1))
    model.add(BatchNormalization())
    model.add(ReLU())
    model.add(AveragePooling2D((2, 2)))

    model.add(Conv2D(32, (3, 3)))
    model.add(BatchNormalization())
    model.add(ReLU())

    model.add(Conv2D(64, (3, 3)))
    model.add(BatchNormalization())
    model.add(ReLU())

    model.add(Flatten())
    model.add(Dense(100, activation='relu'))
    model.add(Dense(1, activation='linear'))

    # Compile the model
    model.compile(optimizer=Adam(learning_rate=0.001), loss=mean_absolute_percentage_square_error)
    # model.summary()

    return model
