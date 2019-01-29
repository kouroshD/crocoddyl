import unittest
from crocoddyl import ActionModelNumDiff
from crocoddyl import ActionModelUnicycle, ActionModelUnicycleVar
import numpy as np



class ActionModelTestCase(unittest.TestCase):
    MODEL = None
    MODEL_NUMDIFF = None

    def setUp(self):
        # Creating NumDiff action model
        self.MODEL_NUMDIFF = ActionModelNumDiff(self.MODEL, withGaussApprox=True)

        # Creating the action data
        self.DATA = self.MODEL.createData()
        self.DATA_NUMDIFF = self.MODEL_NUMDIFF.createData()

    def test_calc_retunrs_state(self):
        # Generating random state and control vectors
        x = self.MODEL.State.rand()
        u = np.random.rand(self.MODEL.nu)

        # Getting the state dimension from calc() call
        nx = self.MODEL.calc(self.DATA, x, u)[0].shape

        # Checking the dimension for the state and its tangent
        self.assertEqual(nx, (self.MODEL.nx,), \
            "Dimension of state vector is wrong.")

    def test_calc_returns_a_cost(self):
        # Getting the cost value computed by calc()
        x = self.MODEL.State.rand()
        u = np.random.rand(self.MODEL.nu)
        cost = self.MODEL.calc(self.DATA, x, u)[1]

        # Checking that calc returns a cost value
        self.assertTrue(isinstance(cost,float), \
            "calc() doesn't return a cost value.")

    def test_partial_derivatives_against_numdiff(self):
        # Generating random values for the state and control
        x = self.MODEL.State.rand()
        u = np.random.rand(self.MODEL.nu)

        # Computing the action derivatives
        self.MODEL.calcDiff(self.DATA,x,u)
        self.MODEL_NUMDIFF.calcDiff(self.DATA_NUMDIFF,x,u)

        # Checking the partial derivatives against NumDiff
        tol = 10*self.MODEL_NUMDIFF.disturbance
        self.assertTrue(np.allclose(self.DATA.Fx,self.DATA_NUMDIFF.Fx, atol=tol), \
            "Fx is wrong.")
        self.assertTrue(np.allclose(self.DATA.Fu,self.DATA_NUMDIFF.Fu, atol=tol), \
            "Fu is wrong.")
        self.assertTrue(np.allclose(self.DATA.Lx,self.DATA_NUMDIFF.Lx, atol=tol), \
            "Fx is wrong.")
        self.assertTrue(np.allclose(self.DATA.Lu,self.DATA_NUMDIFF.Lu, atol=tol), \
            "Fx is wrong.")
        self.assertTrue(np.allclose(self.DATA.Lxx,self.DATA_NUMDIFF.Lxx, atol=tol), \
            "Fx is wrong.")
        self.assertTrue(np.allclose(self.DATA.Lxu,self.DATA_NUMDIFF.Lxu, atol=tol), \
            "Fx is wrong.")
        self.assertTrue(np.allclose(self.DATA.Luu,self.DATA_NUMDIFF.Luu, atol=tol), \
            "Fx is wrong.")


class UnicycleTest(ActionModelTestCase):
    ActionModelTestCase.MODEL = ActionModelUnicycle()

class UnicycleVarTest(ActionModelTestCase):
    ActionModelTestCase.MODEL = ActionModelUnicycleVar()

    def test_rollout_against_unicycle(self):
        # Creating the Unycicle action model
        X = self.MODEL.State
        model0 = ActionModelUnicycle()
        data0 = model0.createData()

        # Generating random values for the state and control vectors
        x = X.rand()
        x0 = X.diff(X.zero(),x)
        u = np.random.rand(self.MODEL.nu)

        # Making the rollout
        xnext,cost = self.MODEL.calc(self.DATA,x,u)
        xnext0,cost0 = model0.calc(data0,x0,u)

        # Checking the rollout (next state) and cost values
        self.assertTrue(
            np.allclose(X.integrate(X.zero(),xnext0), xnext, atol=1e-9), \
            "Dynamics simulation is wrong.")
        self.assertAlmostEqual(cost0, cost, "Cost computation is wrong.")

# TODO create testcases for a general cost function and specific model
# for this is needed a sort of DifferentialActionModelPositioning
# Later test_costs might merged inside this code.



if __name__ == '__main__':
    unittest.main()