from nofars_functions import *


class TestNofarsFunctions:
    """ A couple of tests for nofars_functions """

    def test_connection_init(self):
        conn = Connection()
        assert isinstance(conn, Connection)

    def test_sample_device(self):
        conn = Connection(board_number=0,
                          channel_number=0,
                          max_pressure=0,
                          min_pressure=0,
                          factor=0)
        value = conn.sample_device(board_num=conn.board_number)
        assert isinstance(value, float)
        assert not np.isnan(value)

    def test_normalize_value(self):
        values = range(100)
        extremes = [0, 100]
        for value in values:
            normalized_value = normalize_value(value, extremes)
            assert isinstance(normalized_value, float)
            assert normalized_value == (value - extremes[0]) / (extremes[1] - extremes[0])

    def test_volt_to_newton(self):
        conn = Connection(board_number=0,
                          channel_number=0,
                          max_pressure=0,
                          min_pressure=0,
                          factor=2.5)
        values = range(100)
        for value in values:
            newton_value = volt_to_newton(value, conn.volt_to_newton_factor)
            assert newton_value == value * conn.volt_to_newton_factor

    def test_parse_client_init_message(self):
        init_message = "2_LW36908,3_LW36907,8_LW36910"
        target_channels = [2, 3, 8]
        connections = parse_client_init_message(init_message)
        assert isinstance(connections, list)
        for index, connection in enumerate(connections):
            assert isinstance(connection, Connection)
            assert connection.channel_number == target_channels[index]


if __name__ == "__main__":
    test = TestNofarsFunctions()
    test.test_connection_init()
    test.test_sample_device()
    test.test_normalize_value()
    test.test_volt_to_newton()
    test.test_parse_client_init_message()

    print("Test successful!")
