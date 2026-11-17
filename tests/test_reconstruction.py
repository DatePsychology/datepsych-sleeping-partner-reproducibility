"""Unittest verification of aggregate arithmetic and figure inputs.

Run from repository root: python -m unittest discover -s tests -v
No participant-level dataset is present or implied.
"""
import math
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import reproduce_sleep_figures as rep


class ReconstructionTests(unittest.TestCase):
    def setUp(self):
        self.s=rep.group_sizes()

    def test_unique_current_group_reconstruction(self):
        self.assertEqual(len(rep.reconstruct_size_candidates()),1)
        self.assertEqual((self.s['men'],self.s['women']),(1009,334))
        self.assertEqual((self.s['current_men'],self.s['current_women']),(681,240))
        self.assertEqual((self.s['current_woken_men'],self.s['current_woken_women']),(453,154))

    def test_current_waking_matches_reported_chi(self):
        c=rep.chi_stats(453,681,154,240)
        self.assertAlmostEqual(c['yates_chi'],0.33887,places=4)
        self.assertAlmostEqual(c['yates_p'],0.5605,places=3)

    def test_current_assault_differs_from_published_p_one(self):
        c=rep.chi_stats(3,453,5,154)
        self.assertAlmostEqual(c['yates_p'],0.0433247555,places=7)
        self.assertAlmostEqual(c['fisher_p'],0.0281631251,places=7)

    def test_flirting_possible_missingness_explanation(self):
        c=rep.chi_stats(451,681,134,236)
        self.assertAlmostEqual(c['yates_chi'],6.368518,places=5)
        self.assertAlmostEqual(c['yates_p'],0.01162,places=4)

    def test_past_waking_rounding_sensitivity(self):
        self.assertEqual(self.s['past_woken_women_candidates'],[219,220,221])
        rows=rep.past_waking_rounding(self.s)
        for r in rows:
            self.assertLess(float(r['reconstructed_yates_p']),0.00002)
            self.assertGreater(float(r['reconstructed_yates_chi']),18)
        self.assertAlmostEqual(rep.chi_stats(515,839,220,289)['yates_chi'],19.933601,places=5)

    def test_past_assault_nearly_exact_reproduction(self):
        c=rep.chi_stats(14,830,46,280)
        self.assertAlmostEqual(c['yates_chi'],86.126,places=3)
        self.assertAlmostEqual(100*(1-14/830),98.3,places=1)
        self.assertAlmostEqual(100*(1-46/280),83.6,places=1)

    def test_current_women_evaluation_has_no_exposure_denominator(self):
        r=rep.valid_triplets(154,[62.1,27.1,10.8],[1,1,1])
        self.assertEqual(r,[])
        candidates=rep.valid_triplets(240,[62.1,27.1,10.8],[1,1,1])
        self.assertIn((240,149,65,26),candidates)

    def test_past_women_evaluation_194_is_candidate(self):
        candidates=rep.valid_triplets(220,[63.4,24.7,11.9],[1,1,1])
        self.assertIn((194,123,48,23),candidates)

    def test_wilcoxon_convention_bounds(self):
        w=rep.wilcoxon_checks(self.s)
        r={x['label']:x for x in w}
        for name in ('current positivity, exposed','female satisfaction, exposed vs not','past positivity, exposed'):
            self.assertFalse(r[name]['W_compatible_with_U'])
            self.assertFalse(r[name]['W_compatible_raw_rank_1'])
            self.assertFalse(r[name]['W_compatible_raw_rank_2'])
        self.assertTrue(r['current positivity, all partnered alternative']['W_compatible_raw_rank_2'])
        self.assertFalse(r['male satisfaction, exposed vs not']['W_compatible_raw_rank_1'])
        self.assertTrue(r['male satisfaction, exposed vs not']['W_compatible_raw_rank_2'])

    def test_published_inferential_test_count(self):
        rows=rep.read_csv('published_tests.csv')
        self.assertEqual(len(rows),9)
        self.assertEqual(len({r['key'] for r in rows}),9)

    def test_drouin_figure_bars_from_published_table(self):
        _,_,data=rep.fig_data(self.s)
        look={(r['response'],r['group']):r for r in data}
        for title,sex,cases,n,rounded in [
            ('Started actively participating','partner',94,143,65.7),
            ('Started actively participating','nonpartner',4,29,13.8),
            ('Allowed to finish but did not participate','partner',26,143,18.2),
            ('Allowed to finish but did not participate','nonpartner',4,29,13.8),
            ('Told them to stop, but they did not stop','partner',9,143,6.3),
            ('Told them to stop, but they did not stop','nonpartner',6,29,20.7),
            ('Told partner wanted it again','partner',66,143,46.2),
            ('Told partner wanted it again','nonpartner',2,29,6.9),
        ]:
            r=look[(title,sex)]
            self.assertEqual((r['cases'],r['denominator']),(cases,n))
            self.assertAlmostEqual(r['percent'],100*cases/n,places=8)
            self.assertAlmostEqual(r['percent'],rounded,delta=0.05)

    def test_wilson_intervals_are_in_valid_range(self):
        for k,n in [(515,839),(220,289)]:
            lo,hi=rep.wilson_interval(k,n)
            self.assertTrue(0<lo<k/n<hi<1)

if __name__=='__main__':
    unittest.main()
