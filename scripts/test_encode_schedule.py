import contextlib
import io
import json
import os
import tempfile
import unittest

from encode_schedule import KEY, decode, encode, main


class EncodeTest(unittest.TestCase):
    def test_round_trip(self):
        self.assertEqual(decode(encode(['taron-phantasialand'], KEY), KEY), ['taron-phantasialand'])

    def test_not_plain_text(self):
        out = json.dumps(encode(['taron-phantasialand'], KEY))
        self.assertNotIn('taron', out)

    def test_rejects_unknown_ids(self):
        with tempfile.TemporaryDirectory() as tmp:
            sched, coasters, out = (os.path.join(tmp, n) for n in ('s.json', 'c.json', 'o.json'))
            json.dump({'ids': ['taron-phantasialand', 'made-up']}, open(sched, 'w'))
            json.dump({'coasters': [{'id': 'taron-phantasialand', 'path': 'M1,1 L2,2'}]}, open(coasters, 'w'))
            with self.assertRaises(SystemExit) as e, contextlib.redirect_stderr(io.StringIO()):
                main(sched, coasters, out)
            self.assertNotEqual(e.exception.code, 0)
            self.assertFalse(os.path.exists(out))

    def test_rejects_ids_without_outline(self):
        with tempfile.TemporaryDirectory() as tmp:
            sched, coasters, out = (os.path.join(tmp, n) for n in ('s.json', 'c.json', 'o.json'))
            json.dump({'ids': ['nowhere']}, open(sched, 'w'))
            json.dump({'coasters': [{'id': 'nowhere', 'path': None}]}, open(coasters, 'w'))
            with self.assertRaises(SystemExit), contextlib.redirect_stderr(io.StringIO()):
                main(sched, coasters, out)


if __name__ == '__main__':
    unittest.main()
