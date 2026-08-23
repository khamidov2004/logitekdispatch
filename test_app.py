import unittest
from app import format_dispatch_message

class TestDispatchFormatting(unittest.TestCase):
    def test_single_leg_with_pu_and_ref(self):
        """Single-leg load with PU# and REF# present."""
        sample_data = {
            "broker": "WEL Companies",
            "load_id": "187338",
            "pickup_number": "WEL-5544",
            "ref_number": "REF-9988",
            "pickup": {
                "date": "10/27",
                "time": "FCFS",
                "facility_name": "STUMLER FARMS",
                "full_address": "7313 W US HIGHWAY 150, FREDERICKSBURG IN"
            },
            "delivery": {
                "date": "10/28",
                "time": "06:00",
                "facility_name": "PUBLIX LAKELAND",
                "full_address": "3145 NEW TAMPA HWY, LAKELAND FL 33815"
            },
            "rate": "3100"
        }
        output = format_dispatch_message(sample_data)

        self.assertIn("Broker: WEL Companies", output)
        self.assertIn("LOAD ID : 187338", output)
        self.assertIn("PU#  WEL-5544", output)
        self.assertIn("REF#  REF-9988", output)
        self.assertIn("PU time : FCFS  10/27", output)
        self.assertIn("PU #  WEL-5544", output)
        self.assertIn("STUMLER FARMS", output)
        self.assertIn("DEL time : 06:00   10/28", output)
        self.assertIn("PUBLIX LAKELAND", output)
        self.assertIn("RATE: 3100$", output)

    def test_single_leg_without_pu_and_ref(self):
        """Single-leg load WITHOUT PU# and REF# — labels present, values blank."""
        sample_data = {
            "broker": "WEL Companies",
            "load_id": "187338",
            "pickup": {
                "date": "10/27",
                "time": "FCFS",
                "facility_name": "STUMLER FARMS",
                "full_address": "7313 W US HIGHWAY 150, FREDERICKSBURG IN"
            },
            "delivery": {
                "date": "10/28",
                "time": "06:00",
                "facility_name": "PUBLIX LAKELAND",
                "full_address": "3145 NEW TAMPA HWY, LAKELAND FL 33815"
            },
            "rate": "3100"
        }
        output = format_dispatch_message(sample_data)
        self.assertIn("PU#  \n", output)
        self.assertIn("REF#  \n", output)

    def test_round_trip_reload(self):
        """Round trip with RELOAD — PU# for each stop extracted."""
        sample_data = {
            "broker": "RXO",
            "load_id": "23870304",
            "pickup_number": "23046522",
            "is_round_trip": True,
            "stops": [
                {
                    "type": "PU",
                    "date": "08/17",
                    "time": "13:00",
                    "pickup_number": "23046522",
                    "facility_name": "Nutrition & Bioscience",
                    "full_address": "6 McJunkin Rd\nNitro, WV 25143"
                },
                {
                    "type": "RELOAD",
                    "date": "8/18",
                    "time": "08:00 15:00",
                    "pickup_number": "23046946",
                    "facility_name": "Sterigenics",
                    "full_address": "75 Tilbury Rd\nSalem, NJ 08079"
                },
                {
                    "type": "DEL",
                    "date": "8/19",
                    "time": "08:15",
                    "facility_name": "Nutrition & Bioscience",
                    "full_address": "6 McJunkin Rd\nNitro, WV 25143"
                }
            ],
            "rate": "3937.0"
        }
        output = format_dispatch_message(sample_data)

        # 1 PU, 1 DEL → no numbering (PU, not PU1)
        self.assertIn("PU time : 13:00  08/17", output)
        self.assertIn("PU #  23046522", output)
        self.assertIn("PU location :", output)

        # RELOAD block consolidated
        self.assertIn("RELOAD time : 08:00 15:00   08/18", output)
        self.assertIn("PU # 23046946", output)
        self.assertNotIn("RELOAD location", output)

        # DEL block
        self.assertIn("DEL time : 08:15", output)
        self.assertIn("DEL location :", output)
        self.assertIn("RATE: 3937$", output)

    def test_multi_pu_multi_del(self):
        """Multi-stop: 2 PUs and 2 DELs → PU1, PU2, DEL1, DEL2."""
        sample_data = {
            "broker": "Echo",
            "load_id": "ECH-999",
            "pickup_number": "PU-111",
            "ref_number": "REF-222",
            "is_round_trip": True,
            "stops": [
                {
                    "type": "PU",
                    "date": "09/01",
                    "time": "06:00",
                    "pickup_number": "PU-111",
                    "facility_name": "Warehouse Alpha",
                    "full_address": "100 Main St, Newark, NJ 07101"
                },
                {
                    "type": "PU",
                    "date": "09/01",
                    "time": "12:00",
                    "pickup_number": "PU-222",
                    "facility_name": "Warehouse Beta",
                    "full_address": "200 Oak Ave, Trenton, NJ 08601"
                },
                {
                    "type": "DEL",
                    "date": "09/02",
                    "time": "08:00",
                    "facility_name": "Depot Charlie",
                    "full_address": "300 Elm Rd, Baltimore, MD 21201"
                },
                {
                    "type": "DEL",
                    "date": "09/02",
                    "time": "14:00",
                    "facility_name": "Depot Delta",
                    "full_address": "400 Pine St, DC 20001"
                }
            ],
            "rate": "4500"
        }
        output = format_dispatch_message(sample_data)

        # PU1 and PU2 (numbered because 2 PUs)
        self.assertIn("PU1 time : 06:00  09/01", output)
        self.assertIn("PU1 location :", output)
        self.assertIn("Warehouse Alpha", output)

        self.assertIn("PU2 time : 12:00  09/01", output)
        self.assertIn("PU2 location :", output)
        self.assertIn("Warehouse Beta", output)

        # DEL1 and DEL2 (numbered because 2 DELs)
        self.assertIn("DEL1 time : 08:00   09/02", output)
        self.assertIn("DEL1 location :", output)
        self.assertIn("Depot Charlie", output)

        self.assertIn("DEL2 time : 14:00   09/02", output)
        self.assertIn("DEL2 location :", output)
        self.assertIn("Depot Delta", output)

        # Header
        self.assertIn("PU#  PU-111", output)
        self.assertIn("REF#  REF-222", output)
        self.assertIn("RATE: 4500$", output)

    def test_empty_data(self):
        """Empty data — all fields N/A, PU# and REF# labels present but blank."""
        output = format_dispatch_message({})
        self.assertIn("Broker: N/A", output)
        self.assertIn("LOAD ID : N/A", output)
        self.assertIn("PU#  \n", output)
        self.assertIn("REF#  \n", output)

if __name__ == "__main__":
    unittest.main()
