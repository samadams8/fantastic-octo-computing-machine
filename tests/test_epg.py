import unittest

import torch

from mritorch import epg

_atol = 1e-6  # Absolute tolerance for allclose

class TestExcitation(unittest.TestCase):
    def test_Tx180(self):
        Tx180 = epg.excitation_operator(180)
        truth = torch.tensor([
            [0, 1, 0],
            [1, 0, 0],
            [0, 0, -1]
        ], dtype=torch.cfloat)

        self.assertEqual(Tx180.shape, (3, 3))
        self.assertTrue(torch.allclose(Tx180, truth, atol=_atol))

    def test_Tx90(self):
        Tx90 = epg.excitation_operator(90)
        truth = torch.tensor([
            [0.5, 0.5, -1j],
            [0.5, 0.5, +1j],
            [-0.5j, +0.5j, 0]
        ], dtype=torch.cfloat)

        self.assertEqual(Tx90.shape, (3, 3))
        self.assertTrue(torch.allclose(Tx90, truth, atol=_atol))

    def test_Ty90(self):
        Ty90 = epg.excitation_operator(90, 90)
        truth = torch.tensor([
            [0.5, -0.5, 1],
            [-0.5, 0.5, 1],
            [-0.5, -0.5, 0]
        ], dtype=torch.cfloat)

        self.assertEqual(Ty90.shape, (3, 3))
        self.assertTrue(torch.allclose(Ty90, truth, atol=_atol))

    def test_Ty180(self):
        Ty90 = epg.excitation_operator(180, 90)
        truth = torch.tensor([
            [0, -1, 0],
            [-1, 0, 0],
            [0, 0, -1]
        ], dtype=torch.cfloat)

        self.assertEqual(Ty90.shape, (3, 3))
        self.assertTrue(torch.allclose(Ty90, truth, atol=_atol))

    def test_multi(self):
        flip_angle = torch.tensor([45, 90, 180, 45, 90, 180, 45, 90, 180])
        phase_angle = torch.tensor([0, 0, 0, 45, 45, 45, 90, 90, 90])
        Tx = epg.excitation_operator(flip_angle, phase_angle=phase_angle)
        truth = torch.stack([
            epg.excitation_operator(flip_angle[i], phase_angle[i])
            for i in range(flip_angle.shape[0])
        ])

        self.assertEqual(Tx.shape, (9, 3, 3))
        self.assertTrue(torch.allclose(Tx, truth, atol=_atol))

class TestRelaxation(unittest.TestCase):
    def test_defaults(self):
        Erelax, Erecovery = epg.relaxation_operator(1)
        truth_relax = torch.tensor([1, 1, 1], dtype=torch.float)
        truth_recovery = torch.tensor([0, 0, 0], dtype=torch.float)

        self.assertEqual(Erelax.shape, (3,))
        self.assertTrue(torch.allclose(Erelax, truth_relax, atol=_atol))

        self.assertEqual(Erecovery.shape, (3,))
        self.assertTrue(torch.allclose(Erecovery, truth_recovery, atol=_atol))
    
    def test_T1(self):
        T1vals = torch.tensor([10, 30, 100, 300, 1000, 3000], dtype=torch.float)
        Erelax, Erecovery = epg.relaxation_operator(1, T1=T1vals)
        E1 = torch.exp(-1 / T1vals)
        E2 = torch.ones_like(E1)
        Zs = torch.zeros_like(E1)
        truth_relax = torch.stack([E2, E2, E1], dim=-1)
        truth_recovery = torch.stack([Zs, Zs, (1 - E1)], dim=-1)

        self.assertEqual(Erelax.shape, (6, 3,))
        self.assertTrue(torch.allclose(Erelax, truth_relax, atol=_atol))

        self.assertEqual(Erecovery.shape, (6, 3,))
        self.assertTrue(torch.allclose(Erecovery, truth_recovery, atol=_atol))

    def test_T2(self):
        T2vals = torch.tensor([1, 3, 10, 30, 100, 300, 1000, 3000], dtype=torch.float)
        Erelax, Erecovery = epg.relaxation_operator(1, T2=T2vals)
        E2 = torch.exp(-1 / T2vals)
        E1 = torch.ones_like(E2)
        Zs = torch.zeros_like(E2)
        truth_relax = torch.stack([E2, E2, E1], dim=-1)
        truth_recovery = torch.stack([Zs, Zs, (1 - E1)], dim=-1)

        self.assertEqual(Erelax.shape, (8, 3,))
        self.assertTrue(torch.allclose(Erelax, truth_relax, atol=_atol))

        self.assertEqual(Erecovery.shape, (8, 3,))
        self.assertTrue(torch.allclose(Erecovery, truth_recovery, atol=_atol))

    def test_M0(self):
        M0vals = torch.tensor([0.1, 0.3, 1, 3, 10, 30], dtype=torch.float)
        T1vals = torch.tensor([10, 30, 100, 300, 1000, 3000], dtype=torch.float)
        Erelax, Erecovery = epg.relaxation_operator(1, T1=T1vals, M0=M0vals)
        E1 = torch.exp(-1 / T1vals)
        E2 = torch.ones_like(E1)
        Zs = torch.zeros_like(E1)
        truth_relax = torch.stack([E2, E2, E1], dim=-1)
        truth_recovery = torch.stack([Zs, Zs, M0vals * (1 - E1)], dim=-1)

        self.assertEqual(Erelax.shape, (6, 3,))
        self.assertTrue(torch.allclose(Erelax, truth_relax, atol=_atol))

        self.assertEqual(Erecovery.shape, (6, 3,))
        self.assertTrue(torch.allclose(Erecovery, truth_recovery, atol=_atol))

    def test_dt(self):
        dt = torch.tensor([1, 2, 3, 4, 5, 6], dtype=torch.float)
        Erelax, Erecovery = epg.relaxation_operator(dt)
        truth_relax = torch.stack([torch.ones_like(dt), torch.ones_like(dt), torch.ones_like(dt)], dim=-1)
        truth_recovery = torch.stack([torch.zeros_like(dt), torch.zeros_like(dt), torch.zeros_like(dt)], dim=-1)

        self.assertEqual(Erelax.shape, (6, 3,))
        self.assertTrue(torch.allclose(Erelax, truth_relax, atol=_atol))

        self.assertEqual(Erecovery.shape, (6, 3,))
        self.assertTrue(torch.allclose(Erecovery, truth_recovery, atol=_atol))

    def test_multi(self):
        dt = torch.tensor([1, 2, 3, 4, 5, 6], dtype=torch.float)
        T1vals = torch.tensor([10, 30, 100, 300, 1000, 3000], dtype=torch.float)
        T2vals = torch.tensor([1, 3, 10, 30, 100, 300], dtype=torch.float)
        M0vals = torch.tensor([0.1, 0.3, 1, 3, 10, 30], dtype=torch.float)
        Erelax, Erecovery = epg.relaxation_operator(dt, T1=T1vals, T2=T2vals, M0=M0vals)
        E1 = torch.exp(-dt / T1vals)
        E2 = torch.exp(-dt / T2vals)
        Zs = torch.zeros_like(E1)
        truth_relax = torch.stack([E2, E2, E1], dim=-1)
        truth_recovery = torch.stack([Zs, Zs, M0vals * (1 - E1)], dim=-1)

        self.assertEqual(Erelax.shape, (6, 3,))
        self.assertTrue(torch.allclose(Erelax, truth_relax, atol=_atol))

        self.assertEqual(Erecovery.shape, (6, 3,))
        self.assertTrue(torch.allclose(Erecovery, truth_recovery, atol=_atol))

class TestDephase(unittest.TestCase):
    def test_shifts(self):
        s = torch.arange(15).view(3, 5)

        shifted = epg.dephase(s, 0)
        truth = torch.tensor([
            [0, 1, 2, 3, 4],
            [5, 6, 7, 8, 9],
            [10, 11, 12, 13, 14]
        ])
        self.assertTrue(torch.allclose(shifted, truth, atol=_atol))

        shifted = epg.dephase(s, 1)
        truth = torch.tensor([
            [6, 0, 1, 2, 3],
            [6, 7, 8, 9, 0],
            [10, 11, 12, 13, 14]
        ])
        self.assertTrue(torch.allclose(shifted, truth, atol=_atol))

        shifted = epg.dephase(s, 2)
        truth = torch.tensor([
            [7, 6, 0, 1, 2],
            [7, 8, 9, 0, 0],
            [10, 11, 12, 13, 14]
        ])
        self.assertTrue(torch.allclose(shifted, truth, atol=_atol))

        shifted = epg.dephase(s, -1)
        truth = torch.tensor([
            [1, 2, 3, 4, 0],
            [1, 5, 6, 7, 8],
            [10, 11, 12, 13, 14]
        ])
        self.assertTrue(torch.allclose(shifted, truth, atol=_atol))

        shifted = epg.dephase(s, -3)
        truth = torch.tensor([
            [3, 4, 0, 0, 0],
            [3, 2, 1, 5, 6],
            [10, 11, 12, 13, 14]
        ])
        self.assertTrue(torch.allclose(shifted, truth, atol=_atol))

class TestEPG(unittest.TestCase):
    def test_tse(self):
        state = torch.zeros(3, 7, dtype=torch.cfloat)
        state[2,0] = 1

        Ty90 = epg.excitation_operator(90, 90)
        Tx120 = epg.excitation_operator(120, 0)

        state = Ty90 @ state
