import numpy as np
import sys
import os
import re

from mint.IO.burnio import BURN
from mint.objects.BURN import FINITE_BURN

from IPython import embed

def max_attlen(attrlist):
  '''
  max_attlen(attrlist)
  
  Description:
    This function is intended to process a list of strings (attrlist)
  and return the length of the largest string. Originally made to support
  string format spacing.
  
  Inputs:
    attrlist: (list) list of strings
  
  Output:
    maxlen:   (int) length of largest string in the list
  '''
  maxlen = False
  for attr in attrlist:
    if not attr.startswith('_'):
      curlen = len(attr)
      if not maxlen:
        maxlen = curlen
      elif curlen > maxlen:
        maxlen = curlen
      else:
        pass
  return maxlen

class Obj(object):
  '''
    Obj()
    
    Description: Create a generic object, typically as a data container
    
    Inputs:
      None
    
  '''
  def __init__(self,name='obj'):
    self.__name__(name)

  def __name__(self,name):
    self._name = name

  def __repr__(self,val=False):
    number_types   = [float,int,np.float64]
    list_types     = [list,np.array,np.ndarray]
    attrlist = self.__dict__.keys()
    outstr   = '%s Attributes:\n'%self._name
    alen     = max_attlen(attrlist)+3
    for attr in attrlist:
      if not attr.startswith('_'):
        lhs   = ('%s:'%attr).ljust(alen)
        rhs   = self.__dict__[attr]
        vtype = type(rhs)
        if vtype == str:
          # Print out the actual values
          if len(rhs) < 120 and '\n' not in rhs:
            outstr+='\t%s %s %s\n'%(lhs,vtype,rhs)
          else:
            outstr+='\t%s %s *too long for quick display\n'%(lhs,vtype)
        elif vtype == bool:
          outstr+='\t%s %s %s\n'%(lhs,vtype,rhs)
        elif vtype in number_types:
          outstr+='\t%s %s %s\n'%(lhs,vtype,rhs)
        elif vtype == dict:
          outstr+='\t%s %s *not displaying dict contents\n'%(lhs,vtype)
        elif vtype in list_types:
          outstr+='\t%s %s *iterable contents below\n'%(lhs,vtype)
          if len(rhs)<=10:
            for elem in rhs:
              etype = type(elem)
              disp_types = [str,float,int,np.float64]
              if etype in disp_types:
                outstr+='\t\t%s %s\n'%(etype,elem)
              else:
                outstr+='\t\t%s *not displaying this data type\n'%(etype)
          else:
            outstr+='\t\t%s too many elements (%s) to display here\n'%(type(rhs),len(rhs))
        else:
          outstr+='\t%s %s *not displaying this data type\n'%(lhs,vtype)
    return outstr
  
  def gettablen(self,string):
    if len(string) < 4:
      tab = '\t\t\t\t'
    if len(string) < 8:
      tab = '\t\t\t'
    elif len(string) <= 15:
      tab = '\t\t'
    else:
      tab = '\t'
    return tab

class BaseMirageParam(object):
  '''
  '''
  def __init__(self):
    '''
    '''
    self.GROUPS = {}
    return
  
  def __repr__(self):
    '''
    '''
    nlft = 20
    showlist = [x for x in self.__dict__.keys() if not x.startswith('_')]
    gidx = showlist.index('GROUPS')
    showlist.pop(gidx)
    # All Mirage Parameters
    rstr = 'Mirage Parameters:\n'
    for pname in showlist:
      lhs = ('\t%s'%pname).ljust(nlft)
      rhs = self.__dict__[pname]
      rstr+='%s = %s\n'%(lhs,rhs)
    # Parameter Groups
    rstr+='\nParameter Groups:\n'
    for gname in self.GROUPS.keys():
      lhs = ('\t%s'%gname).ljust(nlft)
      rhs = self.GROUPS[gname]
      rstr+='%s = %s\n'%(lhs,rhs)
      
    return rstr

  def init_param(self, pname, dim, group='General', dtype=None, units=None,
                 default=None, desc=None, reference=None, revdate=None):
    '''
    init_param(self,pname,dim,*args)
    
    Inputs:
      pname:      (str) name of the parameter
      dim:        (list) dimensions of parameter. len(dim), the number of 
                        dimensions, corresponds to the number of dimensions of 
                        the parameter.
                        example 1: dim = [99]; 99 indicates allowed to have 
                        99 of this single-value parameter.
                        example 2: dim = [10,99]; 10 indicates an
                        individual value of this parameter is a list of
                        10 values, and 99 indicates allowed to have 99 
                        of these lists.
                        ****JRR: Not yet handling/implementing dimension 
                        length greater than 2****

    
    Optional Args (type):
      group:      (str)
      dtype:      (str)
      units:      (str)
      default:    (any)
      desc:       (str)
      reference:  (str)
      revdate:    (str)
    '''
    ####################################
    # General parameter definition
    self.__dict__[pname] = {}
    self.__dict__[pname]['dim'] = dim
    # Optionals
    if group != None: self.__dict__[pname]['group'] = group
    if dtype != None: self.__dict__[pname]['dtype'] = dtype
    if units != None: self.__dict__[pname]['units'] = units
    if default != None: self.__dict__[pname]['default'] = default
    if desc != None: self.__dict__[pname]['desc'] = desc
    if reference != None: self.__dict__[pname]['reference'] = reference
    if revdate != None: self.__dict__[pname]['revdate'] = revdate
    # Update GROUPS
    if group in self.GROUPS.keys(): self.GROUPS[group].append(pname)
    else: self.GROUPS[group] = [pname]
    return

class FiniteBurn(BaseMirageParam):
  '''
  FiniteBurn(BaseMirageParam)
  
  Source: odp/volume2/links/P-PV-all.html
  
  Description:
    Definitions for all of the parameters included in the MIRAGE 
  MANEUVERS-FINITE model. This class can be initialized as an empty
  finite-burn instance and populated according to each parameter's 
  definition. This makes for reading gin fragments and writing gin
  fragments more consistent and simple.
  '''
  ''' niodump
  DMA1   DP 99
  DMA1TP C10 99
  MA1A   DP  10,99
  MA1K   DP  99
  MA1F   DP  5,99
  MA1M   DP  4,99
  MA1D   DP  99
  C3     DP  99
  DELV   DP  99
  ACELC  DP  3,99
  BURN   I   99
  BRD    I   99
  CMPTF  L   99
  COORS  C12 5,99
  TVDORT I   3,2,99
  LPLANE C6  99
  LDYN   I   99
  ITPEQ  C35 99
  TVTYPE C1  2,99
  TVDORA DP  3,2,99
  TVTRNE DP  99
  TVDGDR DP  3,99
  TVEPS  DP  3,99
  ROLLAX I   99
  SEBURN I   1
  SEVTIM DP  2,100
  SEVENT C30 100
  '''
  def __init__(self):
    '''
    
    Description:
      This class is a definition class for finite-burn parameters. The
    definitions were extracted from MIRAGE documentation.
    '''
    #################################
    # initialize parameter structure
    BaseMirageParam.__init__(self)
    #################################
    # Define Finite-Burn Parameters
    #################################
    # DMA1
    pname = 'DMA1'
    dim   = [99]
    typ   = 'DP'
    grp   = 'FINITE-BURNS'
    unt   = 'seconds past the reference epoch'
    dsc   = 'is the epoch of the start of finite burn i. '
    dsc  += 'The alternate character input is MA1T.'
    self.init_param(pname,dim,group=grp,dtype=typ,units=unt,desc=dsc)
    # DMA1TP
    pname = 'DMA1TP'
    dim   = [99]
    typ   = 'C10'
    grp   = 'FINITE-BURNS'
    unt   = ''
    dsc   = ''
    self.init_param(pname,dim,group=grp,dtype=typ,units=unt,desc=dsc)
    # MA1T
    pname = 'MA1T'
    dim   = [99]
    typ   = 'C35'
    grp   = 'FINITE-BURNS'
    unt   = "'DD-MMM-YYYY hh:mm:ss.ffffffff TYP'"
    dsc   = "MA1T(i) is the epoch of start of finite burn i. The alternate input in seconds is DMA1."
    self.init_param(pname,dim,group=grp,dtype=typ,units=unt,desc=dsc)
    # MA1A
    pname = 'MA1A'
    dim   = [10,99]
    typ   = 'DP'
    grp   = 'FINITE-BURNS'
    unt   = "[deg, deg/sec, deg/sec^2, deg/sec^3, deg/sec^4, deg, deg/sec, deg/sec^2, deg/sec^3, deg/sec^4]"
    dsc   = "MA1A(j,i), (j=1-10), are fourth degree polynomial coefficients of the right ascension (alpha(i)) and declination (delta(i)) of the unit thrust vector in the COORS coordinate system as a function of seconds past the start of finite burn i.\nMA1A(j,i), (j=1-5) are for right ascension.\nMA1A(j,i), (j=6-10) are for declination.\nNote: If finite burn i is under gyro control (ROLLAX(i) 1):\na) If |MA1A(1,i)| 1 then MA1A(j,i), (j=1-3), contains the unit vector in spacecraft coordinates.\nb) If |MA1A(1,i)| > 1 then MA1A(2,i) and MA1A(3,i) are the right ascension and declination in spacecraft coordinates."
    rvd   = "31 January 1996"
    ref   = "Ref: Ekelund, J. E., Blocking and Buffering Records Using LGFIO, IOM 314.9-34, 30 September 1976, pp. 3--103"
    self.init_param(pname,dim,group=grp,dtype=typ,units=unt,desc=dsc,\
                    revdate=rvd,reference=ref)
    # MA1K
    pname = 'MA1K'
    dim   = [99]
    typ   = 'DP'
    grp   = 'FINITE-BURNS'
    unt   = "depends on force units of MA1F"
    dsc   = "MA1K(i) contains unit conversion factors for accelerations of finite burn i. The conversion factor (k) converts the user force (F) / mass (M) system to km/sec (ie km/sec = k(F/M))."
    rvd   = ""
    ref   = ""
    self.init_param(pname,dim,group=grp,dtype=typ,units=unt,desc=dsc,\
                    revdate=rvd,reference=ref)
    # MA1F
    pname = 'MA1F'
    dim   = [5,99]
    typ   = 'DP'
    grp   = 'FINITE-BURNS'
    unt   = "[force, force/sec, force/sec, force/sec, force/sec]"
    dsc   = "MA1F(j,i), (j=1-5), are the fourth degree polynomial coefficients of the thrust of finite burn i as a function of time in seconds past the start of the burn.\n\nNote: Input MA1K(i) converts the accelerations for finite burn i to km/sec. If the force units in MA1F(1-5,i) are in Newtons, then MA1K(i) should be 10."
    rvd   = ""
    ref   = ""
    self.init_param(pname,dim,group=grp,dtype=typ,units=unt,desc=dsc,\
                    revdate=rvd,reference=ref)
    # MA1M
    pname = 'MA1M'
    dim   = [4,99]
    typ   = 'DP'
    grp   = 'FINITE-BURNS'
    unt   = "[kg/sec, (kg/sec)/sec, (kg/sec)/sec, (kg/sec)/sec]"
    dsc   = "MA1M(j,i), (j=1-4) are third degree polynomial coefficients of the mass flow rate for finite burn i as a function of time in seconds past the start time of the burn."
    rvd   = ""
    ref   = ""
    self.init_param(pname,dim,group=grp,dtype=typ,units=unt,desc=dsc,\
                    revdate=rvd,reference=ref)
    # MA1D
    pname = 'MA1D'
    dim   = [99]
    typ   = 'DP'
    grp   = 'FINITE-BURNS'
    unt   = "seconds"
    dsc   = "MA1D(i) is used when BURN(i) is 1, and is the duration of burn i."
    rvd   = ""
    ref   = ""
    self.init_param(pname,dim,group=grp,dtype=typ,units=unt,desc=dsc,\
                    revdate=rvd,reference=ref)
    # DELV
    pname = 'DELV'
    dim   = [99]
    typ   = 'DP'
    grp   = 'FINITE-BURNS'
    unt   = ""
    dsc   = ""
    rvd   = ""
    ref   = ""
    self.init_param(pname,dim,group=grp,dtype=typ,units=unt,desc=dsc,\
                    revdate=rvd,reference=ref)
    # C3
    pname = 'C3'
    dim   = [99]
    typ   = 'DP'
    grp   = 'FINITE-BURNS'
    unt   = ""
    dsc   = ""
    rvd   = ""
    ref   = ""
    self.init_param(pname,dim,group=grp,dtype=typ,units=unt,desc=dsc,\
                    revdate=rvd,reference=ref)
    # BURN
    pname = 'BURN'
    dim   = [99]
    typ   = 'I'
    grp   = 'FINITE-BURNS'
    unt   = "n/a"
    dsc   = "Termination flags for the finite burns.\nBURN(i) = 1 means cut off at the end of the specified time duration, MA1D(i).\nBURN(i) = 2 means cut off after attaining the specified V (change in velocity) in DELV(i).\nBURN(i) = 3 means cut off upon achieving the specified C3(i) (twice the energy per unit mass) referenced to body BRD(i)."
    rvd   = ""
    ref   = ""
    self.init_param(pname,dim,group=grp,dtype=typ,units=unt,desc=dsc,\
                    revdate=rvd,reference=ref)
    # ACELC
    pname = 'ACELC'
    dim   = [3,99]
    typ   = 'DP'
    grp   = 'FINITE-BURNS'
    unt   = ""
    dsc   = ""
    rvd   = ""
    ref   = ""
    self.init_param(pname,dim,group=grp,dtype=typ,units=unt,desc=dsc,\
                    revdate=rvd,reference=ref)
    # COORS
    pname = 'COORS'
    dim   = [5,99]
    typ   = 'C12'
    grp   = 'FINITE-BURNS'
    unt   = "n/a"
    dsc   = "COORS(j,i), (j=1-5) contains the reference center and coordinate system used to compute thrust direction for finite burn i.\nCOORS(1,i) is the body name of the center, used only when the velocity or horizon plane option is used (LPLANE(i) = `VELOC' or `HORIZ').\nCOORS(j,i), (j=2-5) are used only when LPLANE(i) is blank.\nCOORS(2,i) is the direction of the x-axis, `SPACE' or `BODY'.\nCOORS(j,i), (j=3-5), is the description of the x-y plane.\nCOORS(3,i) is the body name.\nCOORS(4,i) is `MEAN' or `TRUE'.\nCOORS(5,i) is `EQUATO' or `ORBITA'."
    rvd   = ""
    ref   = ""
    self.init_param(pname,dim,group=grp,dtype=typ,units=unt,desc=dsc,\
                    revdate=rvd,reference=ref)
    # LPLANE
    pname = 'LPLANE'
    dim   = [99]
    typ   = 'C6'
    grp   = 'FINITE-BURNS'
    unt   = "n/a"
    dsc   = "Reference plane for motor burn pitch and yaw angles."
    rvd   = ""
    ref   = ""
    self.init_param(pname,dim,group=grp,dtype=typ,units=unt,desc=dsc,\
                    revdate=rvd,reference=ref)
    # LDYN
    pname = 'LDYN'
    dim   = [99]
    typ   = 'I'
    grp   = 'FINITE-BURNS'
    unt   = "n/a"
    dsc   = "Reference plane flags; 0, means use static reference plane. not 0, means use dynamic reference plane."
    rvd   = ""
    ref   = ""
    self.init_param(pname,dim,group=grp,dtype=typ,units=unt,desc=dsc,\
                    revdate=rvd,reference=ref)
    # ITPEQ
    pname = 'ITPEQ'
    dim   = [99]
    typ   = 'C35'
    grp   = 'FINITE-BURNS'
    unt   = "n/a"
    dsc   = "ITPEQ(i), (i=1-99) is the epoch of the coordinate system used to compute the thrust direction of finite burn i.\nITPEQ = `DATE' for an of date epoch.\nITPEQ = `1950' for a B1950.0 epoch.\nITPEQ = `2000' for a J2000.0 epoch.\nITPEQ = `DD-MMM-YYYY hh:mm:ss.ffffffff TYP', where TYP is the time type (ET, TAI, UTC, UT1) for the specified epoch.\nThe alternate input in seconds is TPEQ."
    rvd   = ""
    ref   = ""
    self.init_param(pname,dim,group=grp,dtype=typ,units=unt,desc=dsc,\
                    revdate=rvd,reference=ref)
    # BRD
    pname = 'BRD'
    dim   = [99]
    typ   = 'I'
    grp   = 'FINITE-BURNS'
    unt   = ""
    dsc   = ""
    rvd   = ""
    ref   = ""
    self.init_param(pname,dim,group=grp,dtype=typ,units=unt,desc=dsc,\
                    revdate=rvd,reference=ref)
    # CMPTF
    pname = 'CMPTF'
    dim   = [99]
    typ   = 'L'
    grp   = 'FINITE-BURNS'
    unt   = ""
    dsc   = ""
    rvd   = ""
    ref   = ""
    self.init_param(pname,dim,group=grp,dtype=typ,units=unt,desc=dsc,\
                    revdate=rvd,reference=ref)
    # TVDORT
    pname = 'TVDORT'
    dim   = [3,2,99]
    typ   = 'I'
    grp   = 'FINITE-BURNS'
    unt   = ""
    dsc   = ""
    rvd   = ""
    ref   = ""
    self.init_param(pname,dim,group=grp,dtype=typ,units=unt,desc=dsc,\
                    revdate=rvd,reference=ref)
    # TVDORA
    pname = 'TVDORA'
    dim   = [3,2,99]
    typ   = 'DP'
    grp   = 'FINITE-BURNS'
    unt   = ""
    dsc   = ""
    rvd   = ""
    ref   = ""
    self.init_param(pname,dim,group=grp,dtype=typ,units=unt,desc=dsc,\
                    revdate=rvd,reference=ref)
    # TVTRNE
    pname = 'TVTRNE'
    dim   = [99]
    typ   = 'DP'
    grp   = 'FINITE-BURNS'
    unt   = ""
    dsc   = ""
    rvd   = ""
    ref   = ""
    self.init_param(pname,dim,group=grp,dtype=typ,units=unt,desc=dsc,\
                    revdate=rvd,reference=ref)
    # TVDGDR
    pname = 'TVDGDR'
    dim   = [3,99]
    typ   = 'DP'
    grp   = 'FINITE-BURNS'
    unt   = ""
    dsc   = ""
    rvd   = ""
    ref   = ""
    self.init_param(pname,dim,group=grp,dtype=typ,units=unt,desc=dsc,\
                    revdate=rvd,reference=ref)
    # TVEPS
    pname = 'TVEPS'
    dim   = [3,99]
    typ   = 'DP'
    grp   = 'FINITE-BURNS'
    unt   = ""
    dsc   = ""
    rvd   = ""
    ref   = ""
    self.init_param(pname,dim,group=grp,dtype=typ,units=unt,desc=dsc,\
                    revdate=rvd,reference=ref)
    # TVTYPE
    pname = 'TVTYPE'
    dim   = [2,99]
    typ   = 'C1'
    grp   = 'FINITE-BURNS'
    unt   = ""
    dsc   = ""
    rvd   = ""
    ref   = ""
    self.init_param(pname,dim,group=grp,dtype=typ,units=unt,desc=dsc,\
                    revdate=rvd,reference=ref)
    # ROLLAX
    pname = 'ROLLAX'
    dim   = [99]
    typ   = 'I'
    grp   = 'FINITE-BURNS'
    unt   = ""
    dsc   = ""
    rvd   = ""
    ref   = ""
    self.init_param(pname,dim,group=grp,dtype=typ,units=unt,desc=dsc,\
                    revdate=rvd,reference=ref)
    # SEVENT
    pname = 'SEVENT'
    dim   = [100]
    typ   = 'C30'
    grp   = 'FINITE-BURNS'
    unt   = ""
    dsc   = ""
    rvd   = ""
    ref   = ""
    self.init_param(pname,dim,group=grp,dtype=typ,units=unt,desc=dsc,\
                    revdate=rvd,reference=ref)
    # SEVTIM
    pname = 'SEVTIM'
    dim   = [2,100]
    typ   = 'DP'
    grp   = 'FINITE-BURNS'
    unt   = ""
    dsc   = ""
    rvd   = ""
    ref   = ""
    self.init_param(pname,dim,group=grp,dtype=typ,units=unt,desc=dsc,\
                    revdate=rvd,reference=ref)
    # CSEVTM
    pname = 'CSEVTM'
    dim   = [2,100]
    typ   = 'C35'
    grp   = 'FINITE-BURNS'
    unt   = ""
    dsc   = ""
    rvd   = ""
    ref   = ""
    self.init_param(pname,dim,group=grp,dtype=typ,units=unt,desc=dsc,\
                    revdate=rvd,reference=ref)
    return

class IntegrationControl(BaseMirageParam):
  ''' niodump
  DTIM      DP     1
  CENT      I      1
  IC        DP     6
  ORBBND    C6     1
  IORBIT    I      1
  DEND      DP     1
  DRBD      I      1
  DRVL      DP     1
  TMPC      DP     1
  RBOD      I      1
  RVAL      DP     1
  IGTF      I     11
  EPS       DP     1
  EPSV      DP     1
  HMAX      DP     1
  HMIN      DP     1
  LANDH     DP     1
  RSPH      DP    12
  SATSPH    DP    60
  XBSPH     DP    20
  SRCHTM    DP     1
  RUNOUT    I      1
  MAKEPV    L      1
  BASE0     L      1
  RESTRT    L      4
  DELQT     DP     1
  NBQT      I      1
  POLROT    L      1
  CINDIR    L      1
  PVBUG     I      4
  THSHLD    DP     1
  '''
  def __init__(self):
    # initialize parameter structure
    BaseMirageParam.__init__(self)
    
    return

class ImpulsiveBurn(BaseMirageParam):
  ''' niodump
  BRNCRD I   99
  DB1T   DP  99
  DB1TYP C10 99
  MB1V   DP  3,99
  MB1D   DP  99
  MB1P   DP  99
  ITVTYP C2  99
  ITVDRT I   6,99
  ITVDRA DP  6,99
  ITVTRE DP  99
  ITVDGD DP  3,99
  ITVEPS DP  3,99
  IROLLX I   99
  DELVB1 DP  99
  '''
  def __init__(self):
    # initialize parameter structure
    BaseMirageParam.__init__(self)
    
    return

class SmallForces(BaseMirageParam):
  ''' niodump
  SMFTIM DP 1000
  SMFDR  DP 3,1000
  SMFDV  DP 3,1000
  SMFMAS DP 1000
  SMFBAS DP 1000
  SMFCRD I  1
  SMFTYP I  1000
  '''
  def __init__(self):
    # initialize parameter structure
    BaseMirageParam.__init__(self)
    
    return

class Spacecraft(BaseMirageParam):
  ''' niodump
  SCID   I   1
  SCNAME C8  1
  MASS   DP  1
  ACANO  DP  3,40
  DTCANO DP  40
  TTYPE  C12 2
  DTUPRS DP  200
  UPRS   C12 200
  DUPRS  DP  3,200
  REFBS  C12 2,200
  ANGTYP C1  200
  ANGLT  I   3,200
  ANGLS  DP  3,200
  STABLE I   2
  TABVAL DP  2,100
  COMP   C12 10
  CSIZE  DP 2,10
  UPRC   C 24000
  DUPRC  DP 3,200,10
  CANGLE DP 200,10
  CMPTIM DP 20 2?
  USECMP I  100,2 10,2?
  USETAB I  20 2? ???
  MASDEC DP 20 2?
  TOFF   DP 1
  OFFSET DP 3
  SPNDIR DP 3
  SPNRAT DP 1
  TVDILE DP 25 ???
  '''
  def __init__(self):
    # initialize parameter structure
    BaseMirageParam.__init__(self)
    
    return

class AttitudeControl(BaseMirageParam):
  ''' niodump
  DSAT   DP  2,999
  SAAP   DP  9,999
  SCALEQ DP  1
  STREXP DP  100
  STREXT C10 100
  STPEXP DP  100
  STPEXT C10 100
  AR     DP  100
  AX     DP  100
  AY     DP  100
  BB     DP  100
  MCAXIS I   1
  TMC    DP  200
  MCACC  DP  3,200
  '''
  def __init__(self):
    # initialize parameter structure
    BaseMirageParam.__init__(self)
    
    return

class AstrodynamicConstants(BaseMirageParam):
  ''' niodump
  GM     DP 12
  AU     DP 1
  C      DP 1
  PRNAXS DP 3,11
  RADI   DP 12
  OCRADI DP 11
  FLAT   DP 11
  SMA    DP 11
  BETREL DP 1
  GAMREL DP 1
  LREL   DP 1
  PLANGM DP 6
  SATGM  DP 70
  SATPRN DP 3,70 3,60?
  SATR   DP 70
  SATSMA DP 70
  XBGM   DP 20
  XBPRN  DP 3,20
  XBRAD  DP 20
  XBSMA  DP 20
  '''
  def __init__(self):
    # initialize parameter structure
    BaseMirageParam.__init__(self)
    
    return

class SolarPressure(BaseMirageParam):
  ''' niodump
  SRPFLG L   1
  SHDWFL I   1
  SC     DP  1
  SRPTYP C10 1
  SRTTYP C10 1
  SOLCOF DP  1
  SOLTRQ DP  1
  TRQTIM DP  100
  TRQMOD L   100
  REFB   C12 1
  ANGL   DP  1
  SOLSCL DP  10
  SCOFC  DP  4,10
  INDEG  I   1
  TDFC   DP  100,10
  KMNC   SP  4,100,10 
  SRPRA  DP  36
  SRPCL  DP  19
  SRPF   DP  3,36,18,2
  SRPHRM I   2
  SRPFA  DP  3,0:10,0:10,2
  SRPFB  DP  3,10,10,2
  SRTRA  DP  36
  SRTCL  DP  19
  SRTF   DP  3,36,18,2
  SRTHRM I   2
  SRTFA  DP  3,0:10,0:10,2
  SRTFB  DP  3,10,10,2
  '''
  def __init__(self):
    # initialize parameter structure
    BaseMirageParam.__init__(self)
    
    return

class AtmosphericDrag(BaseMirageParam):
  ''' niodump
  IBYATM I  1
  IMDTIM DP 10
  IMDATM I  10
  SCLTIM DP 25
  SCLTYP I  25
  DENSCL DP 2,25
  SCLCOF DP 50
  SCLAMP DP 100
  SCLPHS DP 100
  COFTYP I  1
  DRGSCL DP 10
  DRGTIM DP 100
  SCD    DP 100
  ATMCOF DP 3,10,100
  ATMCLD DP 100
  ODYA   DP 1
  ODYTAB DP 300
  SHS    SP 1
  '''
  def __init__(self):
    # initialize parameter structure
    BaseMirageParam.__init__(self)
    
    return


mirage_keys_read = {}

# Source: MANEUVERS-FINITE.pydat
fb = FiniteBurn()
fb_keys = fb.GROUPS['FINITE-BURNS']
for param in fb_keys:
  mirage_keys_read[param] = 'FINITE-BURNS'

if False:
  pass
  # Source: INITIAL-CONDITIONS.pydat & INITIAL-CONDITIONS-ICG.pydat & INTEGRATION-CONTROL.pydat
  # ic = IntegrationControl()
  # ic_keys = ic.GROUPS['INTEG-CONTRL']
  # for param in ic_keys:
  #   mirage_keys_read[param] = 'INTEG-CONTRL'

  # Source: MANEUVERS-IMPULSIVE.pydat
  # ib = ImpulsiveBurn()
  # ib_keys = ib.GROUPS['INST-BURNS']
  # for param in ib_keys:
  #   mirage_keys_read[param] = 'INST-BURNS'

  # Source: SMALL-FORCES.pydat
  # sf = SmallForces()
  # sf_keys = sf.GROUPS['SMALL-FORCES']
  # for param in sf_keys:
  #   mirage_keys_read[param] = 'SMALL-FORCES'

  # Source: SPACECRAFT.pydat
  # sc = Spacecraft()
  # sc_keys = sc.GROUPS['SPACECRAFT']
  # for param in sc_keys:
  #   mirage_keys_read[param] = 'SPACECRAFT'

  # Source: ATTITUDE-CONTROL.pydat
  # at = AttitudeControl()
  # at_keys = at.GROUPS['ATT-CONTROL']
  # for param in at_keys:
  #   mirage_keys_read[param] = 'ATT-CONTROL'

  # Source: ASTRODYNAMIC-CONSTANTS.pydat
  # ac = AstrodynamicConstants()
  # ac_keys = ac.GROUPS['ASTRO-CONS']
  # for param in ac_keys:
  #   mirage_keys_read[param] = 'ASTRO-CONS'

  # Source: SOLAR-PRESSURE-GENERAL.pydat
  # sp = SolarPressure()
  # sp_keys = sp.GROUPS['SOL-PRESSURE']
  # for param in sp_keys:
  #   mirage_keys_read[param] = 'SOL-PRESSURE'

  # Source: ATMOSPHERIC-DRAG.pydat
  # ad = AtmosphericDrag()
  # ad_keys = ad.GROUPS['ATMOSPHERE']
  # for param in ad_keys:
  #   mirage_keys_read[param] = 'ATMOSPHERE'


notable_groups = {'FINITE-BURNS': FINITE_BURN}
indexed_groups = {'FINITE-BURNS': FINITE_BURN}

# Goal is to take a single value represented as a string from the namelist file,
# and convert it into the appropriate data_type defined in the mirage_param_def
def handle_data_type(val_str, data_type):
  if data_type.startswith('C'):
    max_length = int(data_type[1:])
    if val_str[0] != "'" or val_str[-1] != "'":
      print('ERROR: string value not fully contained in quotes. This is a problem, fix it.')
      print('received: %s'%(val_str.replace('c',',')))
      sys.exit()
    val = val_str[1:-1].replace('c',',')
    if len(val) > max_length:
      print('ERROR: string length exceeds max length set by mirage definitions. This is a problem, fix it.')
      print('received: %s'%(val_str.replace('c',',')))
      print('max length: %i'%(max_length))
      sys.exit()
  elif data_type == 'DP':
    try:
      val = float(val_str)
    except:
      print('ERROR: Invalid float type provided')
      print('recieved: %s'%(val_str.replace('c',',')))
      sys.exit()
  elif data_type == 'I':
    try:
      val = int(val_str)
    except:
      print('ERROR: Invalid int type provided')
      print('recieved: %s'%(val_str.replace('c',',')))
      sys.exit()
  elif data_type == 'L':
    if val_str == '.TRUE.':
      val = True
    elif val_str == '.FALSE.':
      val = False
    else:
      print('ERROR: Invalid boolean type provided, expected .TRUE. or .FALSE.')
      print('recieved: %s'%(val_str.replace('c',',')))
      sys.exit()
  else:
    print('ERROR: Unknown mirage data_type (%s)'%(data_type))
    sys.exit()

  return val

# Goal is to convert n-dimensional indices to a single 1D index so that all n
# dimensions can be accessed from a single 1D list
# Assuming order of depth of indices & data_dim is last, first, middle
def flatten_index(indices, data_dim):
  # note that indices & data_dim are one-indexed, but python is zero-indexed, so
  # flattening the indices to a 1D python list index will involve subtracting 1
  # from the values in indices but not doing so with values in data_dim
  if len(indices) == 0:
    # dimensionless parameters will still be accessed from a list with a single value
    return 0
  elif len(indices) == 1:
    return indices[-1]-1
  elif len(indices) == 2:
    return (indices[-1]-1)*data_dim[-2] + (indices[-2]-1)
  elif len(indices) == 3:
    return (indices[-1]-1)*(data_dim[-2]*data_dim[-3]) + (indices[-2]-1)*data_dim[-3] + (indices[-3]-1)
  else:
    print('ERROR: Not yet handling 4D+ dimensional parameters yet')
    sys.exit()
  
def handle_assignment(gin_dict, assignment):
  # this is only needed for the very first call
  if assignment == '':
    return
  # all lines will have exactly one assignment statement, so this will work
  lhs, rhs = assignment.split('=',1)
  # this will grab the parameter name regardless of whether indices are provided
  param = lhs.split('(')[0]
  
  # param name must be defined in mirage_keys_read, where it will get the group name
  # and get the appropriate mirage docs info from the fb object TODO: more than fb obj
  if param in mirage_keys_read.keys():
    group = mirage_keys_read[param]
    mirage_param_def = getattr(fb,param)
  else:
    print('ERROR: Invalid parameter (%s) provided, please remove from '\
          'namelist file and try again.'%(param))
    sys.exit()
  
  # if indices are provided, store them as a list of ints
  if '(' in lhs:
    if ')' not in lhs:
      print('ERROR: Invalid indices provided for parameter %s, need a closing '\
            'parenthesis for the lhs: %s'%(param,lhs.replace('c',',').replace('x','*')))
      sys.exit()
    indices = lhs.split('(')[1].split(')')[0].split(',')
    indices = list(map(int, indices))
    # mismatch between provided indices dimension and what the mirage docs expect
    if len(indices) != len(mirage_param_def['dim']):
      print('ERROR: Invalid dimensions (%i) used for parameter %s.'%(len(indices),param))
      print('Expected dimension %i based on the MIRAGE parameter definition.'%(len(mirage_param_def['dim'])))
      sys.exit()
  else:
    # if no indices provided, default to first index for every dimension for
    # this parameter (will also work for non-dimensional parameters)
    indices = [1]*len(mirage_param_def['dim'])
  
  
  # Goal is to take a string containing the rhs of an assignment statement, and
  # extract the values into a list, rhs_vals, with the correct data type
  rhs_vals = []
  rhs_vals_str = rhs.split(',')
  # every rhs will end in an extra comma, so ignore the last split
  for val_str in rhs_vals_str[:-1]:
    # remember we replaced * with x since string values could contain * but not lowercase chars
    if 'x' in val_str:
      multiplier, val_str = val_str.split('x',1)
      # extract the data from the val_str into the correct data type
      val = handle_data_type(val_str, mirage_param_def['dtype'])
      # add multiple copies of this data into the rhs_vals list corresponding to
      # the number tied to the * in the namelist
      rhs_vals.extend(int(multiplier)*[val])
    else:
      val = handle_data_type(val_str, mirage_param_def['dtype'])
      rhs_vals.append(val)
  
  flat_index = flatten_index(indices,mirage_param_def['dim'])
  # flat_max represents the total number of values that the parameter can store in 1D
  flat_max = int(np.prod(mirage_param_def['dim']))
  vals_length = len(rhs_vals)
  # all 3 values represent 1D indices now, so we can determine whether the indices of
  # values being attempted to set will be within the limits set by MIRAGE docs
  if vals_length + flat_index > flat_max:
    print('WARNING: exceeded maximum values allowed by parameter, trimming off excess values.')
    vals_length = flat_max - flat_index
    rhs_vals = rhs_vals[:vals_length]
  
  # non-notable groups do not have a custom formatted data object, so use a generic object instead
  if group not in notable_groups.keys():
    if group not in gin_dict.keys():
      gin_dict[group] = Obj()
    if not hasattr(gin_dict[group], param):
      # initialize parameter with the all possible indices flattened to 1D and set to None
      setattr(gin_dict[group], param, [None]*flat_max)
    if len(mirage_param_def['dim']) > 0:
      getattr(gin_dict[group],param)[flat_index:flat_index+vals_length] = rhs_vals
    else:
      setattr(gin_dict[group],param,rhs_vals[0])
  # groups that are indexed like FINITE-BURNS have another level of dictionary with
  # the 1D indices being keys, which requires some messy logic to handle overflow between
  # these indices
  elif group in indexed_groups.keys():
    if group not in gin_dict.keys():
      gin_dict[group] = {}
    # total number of values that the parameter can store past in each 1D index
    flat_max_1D = int(np.prod(mirage_param_def['dim'][:-1]))
    # first lower index in the 2nd-dimension can be some offset from 0
    idx_2D_low = flat_index % flat_max_1D

    if len(mirage_param_def['dim']) > 2:
      flat_max_2D = int(np.prod(mirage_param_def['dim'][:-2]))
      idx_3D_low = idx_2D_low % flat_max_2D
    
    # Calculate the number of 1D indices that will be covered by looking at the number
    # of values to be covered in the first index and then find how many flat_max_1D
    # it would take to cover the rest of the values
    covered_1D_objects = 2 + ((vals_length - (flat_max_1D-idx_2D_low+1)) // flat_max_1D)
    # iterate over each 1D index to be covered
    for i in range(covered_1D_objects):
      # TODO assuming last index is the first dimension for now (true for FINITE-BURNS)
      idx_1D = str(indices[-1]+i).rjust(len(str(mirage_param_def['dim'][-1])),'0')
      # use custom class constructor if not yet initialized
      if idx_1D not in gin_dict[group].keys():
        gin_dict[group][idx_1D] = indexed_groups[group]()
      # if the first 1D index is already covered, other lower indices will always start at 0
      if i != 0:
        idx_2D_low = 0
      # upper index will be the lesser of the remaining values left or the amount
      # that can be stored in a single 1D index
      idx_2D_high = min(vals_length+idx_2D_low,flat_max_1D)
      # ensure that rhs_vals are being "used up" in contiguous order from index 0 to the end
      rhs_vals_offset = len(rhs_vals)-vals_length
      if len(mirage_param_def['dim']) == 3:
        vals_length_3D = idx_2D_high-idx_2D_low
        idx_3D_low = idx_2D_low % flat_max_2D
        covered_2D_objects = 2 + ((vals_length_3D - (flat_max_2D-idx_3D_low+1)) // flat_max_2D)
        offset_2D = idx_2D_low // flat_max_2D
        for j in range(covered_2D_objects):
          if j != 0:
            idx_3D_low = 0
          idx_3D_high = min(vals_length_3D+idx_3D_low,flat_max_2D)
          getattr(gin_dict[group][idx_1D],param)[offset_2D+j][idx_3D_low:idx_3D_high] = rhs_vals[rhs_vals_offset:rhs_vals_offset+(idx_3D_high-idx_3D_low)]
          rhs_vals_offset += idx_3D_high-idx_3D_low
          vals_length_3D -= idx_3D_high-idx_3D_low
          
      elif len(mirage_param_def['dim']) == 2:
        getattr(gin_dict[group][idx_1D],param)[idx_2D_low:idx_2D_high] = rhs_vals[rhs_vals_offset:rhs_vals_offset+(idx_2D_high-idx_2D_low)]
      else:
        # 1D params will just hold a single value for each 1D index
        setattr(gin_dict[group][idx_1D],param,rhs_vals[i])
      # decrement by number of values "used up" in this iteration so the next one will
      # have the appropriate number of vals remaining
      vals_length -= idx_2D_high-idx_2D_low
  else:
    # notable groups that are not indexed groups are handled similarly to non-notable
    # groups with a custom class called
    if group not in gin_dict.keys():
      gin_dict[group] = notable_groups[group]()
    if not hasattr(gin_dict[group], param):
      setattr(gin_dict[group], param, [None]*flat_max)
    if len(mirage_param_def['dim']) > 0:
      getattr(gin_dict[group],param)[flat_index:flat_index+vals_length] = rhs_vals
    else:
      setattr(gin_dict[group],param,rhs_vals[0])
  
  # # Print out parsed contents of file
  # print(assignment.replace('c',',').replace('x','*'))


def read_finiteburn_file(ginnl):
  comsyms = ('!','#','$')
  
  if not os.path.exists(ginnl):
    print('\nERROR: gin namelist file provided does not exist!')
    print('\n%s\n'%ginnl)
    sys.exit()
  
  # Complex data structure with the first level of keys being mirage group names.
  # Most of these group names will point to an object storing the data read in
  # for the parameters in this group.
  # Some more notable group names such as FINITE-BURNS,... will point to another
  # dictionary where the keys will be the first dimension indices (burn number)
  # and each of these index keys will point to a formatted object storing the data
  # read in for the parameters in this group.
  gin_dict = {}
  
  # Will store completed assignment statements cleaned up to unify into a single
  # format. This could span over multiple lines in the namelist file or there
  # could be multiple completed assignment statements in a single line.
  #
  # Once complete, the completed assignment statement is passed onto a helper
  # function handle_assignment() which will turn the statement into the appropriate
  # data type and then store the data in an appropriately defined object in
  # the gin_dict data structure.
  assignment = ''
  
  with open(ginnl,'r') as ifid:
    semicolon_exit = False
    for lnum,line in enumerate(ifid):
      # lines are case-insensitive and have a max length of 80 chars
      line = line[:80].strip().upper()
      
      # skip lines with no comments or data
      if line == '':
        continue
      
      # if first non-whitespace char is ; the namelist file terminates there
      if line[0] == ';':
        break

      # regex to find complete strings within the line
      string_pattern = "'.*?'"
      # stores list of all complete strings in the line
      string_matches = re.findall(string_pattern,line)
      # stores list of the segments of the line between complete strings
      anti_string_matches = re.split(string_pattern,line)
      
      
      # Clean up the segments between complete strings and then alternate merge
      # with the string_matches
      # line_clean will have no whitespaces, comments, strange delimiters will be corrected,
      # and commas inside strings will be replaced with lowercase c since everything is uppercase
      # and asterisks outside strings will be replaced with lowercase x
      line_clean = '' 
      for i,anti_string in enumerate(anti_string_matches):
        # remove all whitespaces and replace asterisks with lowercase x
        anti_string = anti_string.replace(' ','').replace('\t','').replace('*','x')
        # remove all comments (merging stops since a comment lasts till the end of line)
        if any(com in anti_string for com in comsyms):
          comment_pattern = "[!#$].*"
          anti_string = re.sub(comment_pattern,'',anti_string)
          line_clean = f'{line_clean}{anti_string}'
          break
        # there will always be one more anti_string than string, so last iteration needs special case
        elif i == len(anti_string_matches)-1:
          line_clean = f'{line_clean}{anti_string}'
        else:
          # Any char other than space, !, $, #, =, ' acts as a delimiter between strings
          # MIRAGE technically lets = act as a delimiter but it's a PITA to support that here
          # since we need to keep variable assignment statements intact
          if '=' not in anti_string and ',' not in anti_string and len(anti_string) > 0:
            # replace this character with a comma, but not the whole string since
            # that would screw up multiplier syntax such as ITPEQ='2000',98*'2000'
            # could also screw up multi-assignment lines
            anti_string = f',{anti_string[1:]}'
          # alternate merging of strings and anti_strings happens here
          # also replacing of commas in strings with lowercase c
          line_clean = f'{line_clean}{anti_string}{string_matches[i].replace(",","c")}'
      
      # if the original line was purely a comment, we will skip it here
      if line_clean == '':
        continue
      
      # lines ending with a semicolon signal to stop reading the file, but the
      # rest of the current line still needs to be processed
      if line_clean.endswith(';'):
        semicolon_exit = True
        # don't forget to trim the ; off the end before processing
        line_clean = line_clean[:-1]
      
      # force every line to end with a comma to make multiline assignment easier to handle
      if not line_clean.endswith(','):
        line_clean = f'{line_clean},'
      
      # handle multi-assignment lines
      if '=' in line_clean:
        # regex to find the lhs of assignment statements after the start of a line
        assignment_pattern = ",[A-Z].*?="
        # stores list of lhs after the start of the line
        assignment_matches = re.findall(assignment_pattern,line_clean)
        # stores list of everything else including the lhs at the start of the line and all the rhs
        anti_assignment_matches = re.split(assignment_pattern,line_clean)
        
        # iterate over everything else and alternate
        for i,anti_assignment in enumerate(anti_assignment_matches):
          # first iteration will either be just an rhs or the lhs and rhs of the first
          # assignment statement in the line
          if i == 0:
            # line starts with an rhs, so append to the previous lhs at the end of assignment
            if '=' not in anti_assignment:
              assignment = f'{assignment}{anti_assignment}'
            # line starts with an lhs, so append to assignment as a new assignment statement
            else:
              handle_assignment(gin_dict, assignment)
              assignment = anti_assignment
          else:
            # keep a comma at the end of the previous line since we split
            assignment = f'{assignment},'
            handle_assignment(gin_dict, assignment)
            # if multi-assignment is actually present, trim the comma off the
            # start of the lhs and merge with the corresponding rhs before appending
            # to assignment
            assignment = f'{assignment_matches[i-1][1:]}{anti_assignment}'
      # handle multiline assignment by appending line to previous assignment statement
      # stored in assignment list
      else:
        assignment = f'{assignment}{line_clean}'
      
      # found a semicolon at the end of the line earlier, so we'll stop reading
      # the file here since we finished processing the current line
      if semicolon_exit:
        break
  
  # final case needed since no other way of knowing if last assignment is complete
  handle_assignment(gin_dict, assignment)
  
  return gin_dict
  
    
if __name__ == '__main__':
  list_nl = read_finiteburn_file('/home/jason.russell/list.nl')
  # tmp_nl = read_finiteburn_file('/home/jason.russell/tmp.nl')
  embed()
