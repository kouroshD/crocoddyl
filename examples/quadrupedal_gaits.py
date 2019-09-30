import os
import sys

import numpy as np

import crocoddyl
import example_robot_data
import pinocchio
from crocoddyl.utils.quadruped import SimpleQuadrupedalGaitProblem, plotSolution

WITHDISPLAY = 'display' in sys.argv or 'CROCODDYL_DISPLAY' in os.environ
WITHPLOT = 'plot' in sys.argv or 'CROCODDYL_PLOT' in os.environ

# Loading the HyQ model
hyq = example_robot_data.loadHyQ()

# Defining the initial state of the robot
q0 = hyq.model.referenceConfigurations['half_sitting'].copy()
v0 = pinocchio.utils.zero(hyq.model.nv)
x0 = np.concatenate([q0, v0])

# Setting up the 3d walking problem
lfFoot = 'lf_foot'
rfFoot = 'rf_foot'
lhFoot = 'lh_foot'
rhFoot = 'rh_foot'
gait = SimpleQuadrupedalGaitProblem(hyq.model, lfFoot, rfFoot, lhFoot, rhFoot)

# Setting up all tasks
GAITPHASES = [{
    'walking': {
        'stepLength': 0.25,
        'stepHeight': 0.25,
        'timeStep': 1e-2,
        'stepKnots': 25,
        'supportKnots': 2
    }
}, {
    'trotting': {
        'stepLength': 0.15,
        'stepHeight': 0.2,
        'timeStep': 1e-2,
        'stepKnots': 25,
        'supportKnots': 2
    }
}, {
    'pacing': {
        'stepLength': 0.15,
        'stepHeight': 0.2,
        'timeStep': 1e-2,
        'stepKnots': 25,
        'supportKnots': 5
    }
}, {
    'bounding': {
        'stepLength': 0.15,
        'stepHeight': 0.1,
        'timeStep': 1e-2,
        'stepKnots': 25,
        'supportKnots': 5
    }
}, {
    'jumping': {
        'jumpHeight': 0.15,
        'jumpLength': [0.0, 0.3, 0.],
        'timeStep': 1e-2,
        'groundKnots': 10,
        'flyingKnots': 20
    }
}]
cameraTF = [2., 2.68, 0.84, 0.2, 0.62, 0.72, 0.22]

ddp = [None] * len(GAITPHASES)
for i, phase in enumerate(GAITPHASES):
    for key, value in phase.items():
        if key == 'walking':
            # Creating a walking problem
            ddp[i] = crocoddyl.SolverFDDP(
                gait.createWalkingProblem(x0, value['stepLength'], value['stepHeight'], value['timeStep'],
                                          value['stepKnots'], value['supportKnots']))
        elif key == 'trotting':
            # Creating a trotting problem
            ddp[i] = crocoddyl.SolverFDDP(
                gait.createTrottingProblem(x0, value['stepLength'], value['stepHeight'], value['timeStep'],
                                           value['stepKnots'], value['supportKnots']))
        elif key == 'pacing':
            # Creating a pacing problem
            ddp[i] = crocoddyl.SolverFDDP(
                gait.createPacingProblem(x0, value['stepLength'], value['stepHeight'], value['timeStep'],
                                         value['stepKnots'], value['supportKnots']))
        elif key == 'bounding':
            # Creating a bounding problem
            ddp[i] = crocoddyl.SolverFDDP(
                gait.createBoundingProblem(x0, value['stepLength'], value['stepHeight'], value['timeStep'],
                                           value['stepKnots'], value['supportKnots']))
        elif key == 'jumping':
            # Creating a jumping problem
            ddp[i] = crocoddyl.SolverFDDP(
                gait.createJumpingProblem(x0, value['jumpHeight'], value['jumpLength'], value['timeStep'],
                                          value['groundKnots'], value['flyingKnots']))

    # Added the callback functions
    print('*** SOLVE ' + key + ' ***')
    if WITHDISPLAY and WITHPLOT:
        ddp[i].setCallbacks(
            [crocoddyl.CallbackLogger(),
             crocoddyl.CallbackVerbose(),
             crocoddyl.CallbackDisplay(hyq, 4, 4, cameraTF)])
    elif WITHDISPLAY:
        ddp[i].setCallbacks([crocoddyl.CallbackVerbose(), crocoddyl.CallbackVerbose()])
    elif WITHPLOT:
        ddp[i].setCallbacks([
            crocoddyl.CallbackLogger(),
            crocoddyl.CallbackVerbose(),
        ])
    else:
        ddp[i].setCallbacks([crocoddyl.CallbackVerbose()])

    # Solving the problem with the DDP solver
    xs = [hyq.model.defaultState] * len(ddp[i].models())
    us = [m.quasiStatic(d, hyq.model.defaultState) for m, d in list(zip(ddp[i].models(), ddp[i].datas()))[:-1]]
    ddp[i].solve(xs, us, 100, False, 0.1)

    # Defining the final state as initial one for the next phase
    x0 = ddp[i].xs[-1]

# Display the entire motion
if WITHDISPLAY:
    for i, phase in enumerate(GAITPHASES):
        crocoddyl.displayTrajectory(hyq, ddp[i].xs, ddp[i].models()[0].dt)

# Plotting the entire motion
if WITHPLOT:
    xs = []
    us = []
    for i, phase in enumerate(GAITPHASES):
        xs.extend(ddp[i].xs[:-1])
        us.extend(ddp[i].us)
    log = ddp[0].getCallbacks()[0]
    plotSolution(hyq.model, xs, us, figIndex=1, show=False)

    for i, phase in enumerate(GAITPHASES):
        title = phase.keys()[0] + " (phase " + str(i) + ")"
        log = ddp[i].getCallbacks()[0]
        crocoddyl.plotConvergence(log.costs,
                                  log.control_regs,
                                  log.state_regs,
                                  log.gm_stops,
                                  log.th_stops,
                                  log.steps,
                                  figTitle=title,
                                  figIndex=i + 3,
                                  show=True if i == len(GAITPHASES) - 1 else False)