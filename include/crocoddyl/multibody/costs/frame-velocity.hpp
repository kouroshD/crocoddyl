///////////////////////////////////////////////////////////////////////////////
// BSD 3-Clause License
//
// Copyright (C) 2018-2020, LAAS-CNRS, University of Edinburgh
// Copyright note valid unless otherwise stated in individual files.
// All rights reserved.
///////////////////////////////////////////////////////////////////////////////

#ifndef CROCODDYL_MULTIBODY_COSTS_FRAME_VELOCITY_HPP_
#define CROCODDYL_MULTIBODY_COSTS_FRAME_VELOCITY_HPP_
#include "crocoddyl/multibody/fwd.hpp"
#include "crocoddyl/multibody/cost-base.hpp"
#include "crocoddyl/multibody/data/multibody.hpp"
#include "crocoddyl/multibody/frames.hpp"
#include "crocoddyl/core/utils/exception.hpp"

namespace crocoddyl {

template<typename _Scalar>
class CostModelFrameVelocityTpl : public CostModelAbstractTpl<_Scalar> {
 public:
  typedef _Scalar Scalar;
  typedef MathBaseTpl<Scalar> MathBase;
  typedef CostModelAbstractTpl<Scalar> Base;
  typedef StateMultibodyTpl<Scalar> StateMultibody;
  typedef CostDataAbstractTpl<Scalar> CostDataAbstract;
  typedef ActivationModelAbstractTpl<Scalar> ActivationModelAbstract;
  typedef ActivationModelQuadTpl<Scalar> ActivationModelQuad;
  typedef FrameMotionTpl<Scalar> FrameMotion;
  typedef DataCollectorAbstractTpl<Scalar> DataCollectorAbstract;
  typedef typename MathBase::VectorXs VectorXs;
  typedef typename MathBase::Matrix3s Matrix3s;

  CostModelFrameVelocityTpl(boost::shared_ptr<StateMultibody> state,
                         boost::shared_ptr<ActivationModelAbstract> activation,
                         const FrameMotion& Fref,
                         const std::size_t& nu);
  CostModelFrameVelocityTpl(boost::shared_ptr<StateMultibody> state,
                            boost::shared_ptr<ActivationModelAbstract> activation,
                            const FrameMotion& Fref);
  CostModelFrameVelocityTpl(boost::shared_ptr<StateMultibody> state, const FrameMotion& vref, const std::size_t& nu);
  CostModelFrameVelocityTpl(boost::shared_ptr<StateMultibody> state, const FrameMotion& vref);
  ~CostModelFrameVelocityTpl();

  void calc(const boost::shared_ptr<CostDataAbstract>& data,
            const Eigen::Ref<const VectorXs>& x,
            const Eigen::Ref<const VectorXs>& u);
  void calcDiff(const boost::shared_ptr<CostDataAbstract>& data,
                const Eigen::Ref<const VectorXs>& x,
                const Eigen::Ref<const VectorXs>& u);
  boost::shared_ptr<CostDataAbstract> createData(DataCollectorAbstract* const data);

  const FrameMotion& get_vref() const;
  void set_vref(const FrameMotion& vref_in);

protected:
  using Base::state_;
  using Base::activation_;
  using Base::nu_;
  using Base::with_residuals_;
  using Base::unone_;
  
 private:
  FrameMotion vref_;
};


template<typename _Scalar> 
struct CostDataFrameVelocityTpl : public CostDataAbstractTpl<_Scalar> {
  EIGEN_MAKE_ALIGNED_OPERATOR_NEW
  
  typedef _Scalar Scalar;
  typedef MathBaseTpl<Scalar> MathBase;
  typedef CostDataAbstractTpl<Scalar> Base;
  typedef DataCollectorAbstractTpl<Scalar> DataCollectorAbstract;
  typedef typename MathBase::VectorXs VectorXs;
  typedef typename MathBase::MatrixXs MatrixXs;
  typedef typename MathBase::Matrix6xs Matrix6xs;

  template<template<typename Scalar> class Model>
  CostDataFrameVelocityTpl(Model<Scalar>* const model, DataCollectorAbstract* const data)
      : Base(model, data),
        joint(model->get_state()->get_pinocchio().frames[model->get_vref().frame].parent),
        vr(pinocchio::MotionTpl<Scalar>::Zero()),
        fXj(model->get_state()->get_pinocchio().frames[model->get_vref().frame].placement.inverse().toActionMatrix()),
        dv_dq(6, model->get_state()->get_nv()),
        dv_dv(6, model->get_state()->get_nv()),
        Arr_Rx(6, model->get_state()->get_nv()) {
    dv_dq.fill(0);
    dv_dv.fill(0);
    Arr_Rx.fill(0);
    // Check that proper shared data has been passed
    DataCollectorMultibodyTpl<Scalar>* d =
      dynamic_cast<DataCollectorMultibodyTpl<Scalar>* >(shared);
    if (d == NULL) {
      throw_pretty("Invalid argument: the shared data should be derived from DataCollectorMultibody");
    }

    // Avoids data casting at runtime
    pinocchio = d->pinocchio;
  }

  pinocchio::DataTpl<Scalar>* pinocchio;
  pinocchio::JointIndex joint;
  pinocchio::MotionTpl<Scalar> vr;
  typename pinocchio::SE3Tpl<Scalar>::ActionMatrixType fXj;
  Matrix6xs dv_dq;
  Matrix6xs dv_dv;
  Matrix6xs Arr_Rx;

  using Base::shared;
  using Base::activation;
  using Base::cost;
  using Base::Lx;
  using Base::Lu;
  using Base::Lxx;
  using Base::Lxu;
  using Base::Luu;
  using Base::r;
  using Base::Rx;
  using Base::Ru;
  
};

  
}  // namespace crocoddyl

/* --- Details -------------------------------------------------------------- */
/* --- Details -------------------------------------------------------------- */
/* --- Details -------------------------------------------------------------- */
#include "crocoddyl/multibody/costs/frame-velocity.hxx"


#endif  // CROCODDYL_MULTIBODY_COSTS_FRAME_VELOCITY_HPP_
