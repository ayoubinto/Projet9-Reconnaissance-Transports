"""Tests fonctionnels réels. Exécuter après création des modèles et exemples."""
import json,unittest
from pathlib import Path
from streamlit.testing.v1 import AppTest
ROOT=Path(__file__).resolve().parents[1]

@unittest.skipUnless((ROOT/'examples/route_readable.jpg').exists() and (ROOT/'models/stop.pt').exists(),'Modèles/exemples pas encore prêts')
class ApplicationTests(unittest.TestCase):
    def test_ocr_and_persistence(self):
        app=AppTest.from_file(str(ROOT/'app.py'),default_timeout=120).run()
        self.assertFalse(app.exception)
        app.radio[0].set_value('Exemple fourni').run()
        app.selectbox[0].set_value(ROOT/'examples/route_readable.jpg').run()
        app.button[0].click().run()
        self.assertFalse(app.exception);self.assertFalse(app.error)
        before=app.session_state['analysis'][1]
        self.assertTrue(before['ocr_enabled']);self.assertGreater(before['seconds'],0)
        json.dumps(before)
        app.run()
        self.assertEqual(before,app.session_state['analysis'][1]);self.assertFalse(app.error)

    def test_no_ocr_and_threshold_change(self):
        app=AppTest.from_file(str(ROOT/'app.py'),default_timeout=120).run()
        app.radio[0].set_value('Exemple fourni').run()
        app.checkbox[0].uncheck().run();app.button[0].click().run()
        self.assertFalse(app.exception);self.assertFalse(app.error)
        result=app.session_state['analysis'][1];self.assertFalse(result['ocr_enabled'])
        self.assertTrue(all(not d['text'] for d in result['detections']))
        app.slider[0].set_value(.9).run();app.button[0].click().run()
        self.assertFalse(app.error);self.assertFalse(app.exception)
        self.assertEqual(app.session_state['analysis'][0][2],.9)

if __name__=='__main__':unittest.main()
