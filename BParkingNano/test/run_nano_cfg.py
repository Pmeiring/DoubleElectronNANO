from FWCore.ParameterSet.VarParsing import VarParsing
import FWCore.ParameterSet.Config as cms

options = VarParsing('python')

options.register('year', 2023,
    VarParsing.multiplicity.singleton,
    VarParsing.varType.int,
    "Year to process between 2022 or 2023 (default)")

options.register('subera', 0,
    VarParsing.multiplicity.singleton,
    VarParsing.varType.int,
    "Subera of the given year. 0 is preEE (2022) or preBPix (2023), 1 is post~. No difference for 2024")

options.register('isMC', False,
    VarParsing.multiplicity.singleton,
    VarParsing.varType.bool,
    "Run this on real data")

options.register('isSignal', False,
    VarParsing.multiplicity.singleton,
    VarParsing.varType.bool,
    "Run this on signal MC (else J/psi)")

options.register("isMinBias", False,
    VarParsing.multiplicity.singleton,
    VarParsing.varType.bool,
    "Run this on inclusive dilepton MinBias MC")

options.register("isPromptJpsi", False,
    VarParsing.multiplicity.singleton,
    VarParsing.varType.bool,
    "Run this on prompt J/psi MC (else J/psi)")

options.register("isPromptUpsilon", False,
    VarParsing.multiplicity.singleton,
    VarParsing.varType.bool,
    "Run this on prompt Upsilon MC (else J/psi)")

options.register("isElectronFlat", False,
    VarParsing.multiplicity.singleton,
    VarParsing.varType.bool,
    "Run this on flat electron MC (else J/psi)")

options.register("isECALIdealIC", False,
    VarParsing.multiplicity.singleton,
    VarParsing.varType.bool,
    "When running on flat electron MC, use ECAL ideal intercalibrations (real otherwise)")

options.register('wantSummary', True,
    VarParsing.multiplicity.singleton,
    VarParsing.varType.bool,
    "Request summary")

options.register('wantFullRECO', False,
    VarParsing.multiplicity.singleton,
    VarParsing.varType.bool,
    "Save full RECO event")

options.register('saveAllNanoContent', True,
    VarParsing.multiplicity.singleton,
    VarParsing.varType.bool,
    "Store the standard NanoAOD collections")

options.register('reportEvery', 10,
    VarParsing.multiplicity.singleton,
    VarParsing.varType.int,
    "Report every N events")

options.register('skip', 0,
    VarParsing.multiplicity.singleton,
    VarParsing.varType.int,
    "Skip first N events")

options.register('lhcRun', 3,
    VarParsing.multiplicity.singleton,
    VarParsing.varType.int,
    "LHC Run 2 or 3 (default)")

options.register('mode', "reco",
    VarParsing.multiplicity.singleton,
    VarParsing.varType.string,
    "Run standard reco for DoubleEle ('reco') or VBF ('vbf'), efficiency study ('eff'), or trigger matching study ('trg')")

options.register("saveRegressionVars", False,
    VarParsing.multiplicity.singleton,
    VarParsing.varType.bool,
    "Add regression variables to the output")

options.register('version', 'A',
    VarParsing.multiplicity.singleton,
    VarParsing.varType.string,
    "RUN version - A, B, C, D, etc")

options.setDefault('maxEvents', -1)
options.setDefault('tag', '150X')

options.parseArguments()
print(options)

globaltag = None
if options.year==2022:
    globaltag='auto:phase1_2022_realistic' if options.subera==0 else 'auto:phase1_2022_realistic_postEE'
if options.year==2023:
    # globaltag = "130X_mcRun3_2023_realistic_postBPix_v2" if options.isMC else "130X_dataRun3_PromptAnalysis_v1"
    globaltag='auto:phase1_2023_realistic' if options.subera==0 else 'auto:phase1_2023_realistic_postBPix'
if options.year==2024:
    globaltag='auto:phase1_2024_realistic'
if not options.isMC:
    globaltag='auto:run3_data'


ext1 = {False:'data', True:'mc'}
ext2 = {3 : 'Run3', 2 : 'Run2'}
ext3 = {"eff" : "noskim", "reco" : "", "trg" : ""}
ext4 = {True: 'allNano', False: ''}
ext5 = {True: 'withRegVars', False: ''}

output_flags = ["DoubleElectronNANO", ext2[options.lhcRun], str(options.year), ext1[options.isMC]]
if options.mode == "eff":
    output_flags.append(ext3[options.mode])
if options.saveAllNanoContent:
    output_flags.append(ext4[options.saveAllNanoContent])
if options.saveRegressionVars:
    output_flags.append(ext5[options.saveRegressionVars])
output_flags.append(options.tag)

outputFileNANO = cms.untracked.string('_'.join(output_flags)+'.root')

outputFileFEVT = cms.untracked.string('_'.join(['BParkingFullEvt',
                                                str(options.year),
                                                ext1[options.isMC],
                                                options.tag])+'.root')
if not options.inputFiles:
    if options.year == 2022 and options.subera == 0: # PRE-EE
        if options.isMC and options.isSignal:          pass # not implemented
        elif options.isMC and options.isMinBias:
            options.inputFiles = [
            'root://cmsxrootd.fnal.gov///store/mc/Run3Summer22MiniAODv4/InclusiveDileptonMinBias_TuneCP5Plus_13p6TeV_pythia8/MINIAODSIM/validDigi_130X_mcRun3_2022_realistic_v5-v4/2540000/3b3036b2-c738-4b32-b2f2-b3ba86ad0026.root',
            'root://cmsxrootd.fnal.gov///store/mc/Run3Summer22MiniAODv4/InclusiveDileptonMinBias_TuneCP5Plus_13p6TeV_pythia8/MINIAODSIM/validDigi_130X_mcRun3_2022_realistic_v5-v4/2540000/06120290-a3a0-44ea-bd8e-d45d9b8a4306.root',
            'root://cmsxrootd.fnal.gov///store/mc/Run3Summer22MiniAODv4/InclusiveDileptonMinBias_TuneCP5Plus_13p6TeV_pythia8/MINIAODSIM/validDigi_130X_mcRun3_2022_realistic_v5-v4/2540000/98cb2d23-4e66-4afa-baac-ea186cee8c0a.root',
            'root://cmsxrootd.fnal.gov///store/mc/Run3Summer22MiniAODv4/InclusiveDileptonMinBias_TuneCP5Plus_13p6TeV_pythia8/MINIAODSIM/validDigi_130X_mcRun3_2022_realistic_v5-v4/2540000/50097c68-e4cf-4bea-a2c9-3b0b741dc1de.root',
            ]
        elif options.isMC and options.isPromptJpsi:    pass # not implemented
        elif options.isMC and options.isPromptUpsilon: pass # not implemented
        elif options.isMC and options.isElectronFlat and options.isECALIdealIC:
            options.inputFiles = [
            'root://cmsxrootd.fnal.gov///store/mc/Run3Winter22MiniAOD/DoubleElectron_FlatPt-1To500_13p6TeV/MINIAODSIM/FlatPU0to70ECALIdeal_122X_mcRun3_2021_realistic_v9-v3/60000/7bf837da-3304-4c96-901d-42211b796f52.root',
            'root://cmsxrootd.fnal.gov///store/mc/Run3Winter22MiniAOD/DoubleElectron_FlatPt-1To500_13p6TeV/MINIAODSIM/FlatPU0to70ECALIdeal_122X_mcRun3_2021_realistic_v9-v3/60000/cf130663-fa52-4c45-910a-4b74f471984f.root',
            'root://cmsxrootd.fnal.gov///store/mc/Run3Winter22MiniAOD/DoubleElectron_FlatPt-1To500_13p6TeV/MINIAODSIM/FlatPU0to70ECALIdeal_122X_mcRun3_2021_realistic_v9-v3/60000/45207133-41c4-4491-ae48-155fbf212250.root',
            'root://cmsxrootd.fnal.gov///store/mc/Run3Winter22MiniAOD/DoubleElectron_FlatPt-1To500_13p6TeV/MINIAODSIM/FlatPU0to70ECALIdeal_122X_mcRun3_2021_realistic_v9-v3/60000/a0fe60dc-4231-4b16-be2d-6187d4a9ac3c.root',
            ]
        elif options.isMC and options.isElectronFlat:
            options.inputFiles = [
            'root://cmsxrootd.fnal.gov///store/mc/Run3Winter22MiniAOD/DoubleElectron_FlatPt-1To500_13p6TeV/MINIAODSIM/FlatPU0to70_122X_mcRun3_2021_realistic_v9-v2/50000/e332bb2f-ef2a-4b98-a2ad-4defea95069f.root',
            'root://cmsxrootd.fnal.gov///store/mc/Run3Winter22MiniAOD/DoubleElectron_FlatPt-1To500_13p6TeV/MINIAODSIM/FlatPU0to70_122X_mcRun3_2021_realistic_v9-v2/50000/78dbd3b1-fe0f-48a8-b885-df2a65939735.root',
            'root://cmsxrootd.fnal.gov///store/mc/Run3Winter22MiniAOD/DoubleElectron_FlatPt-1To500_13p6TeV/MINIAODSIM/FlatPU0to70_122X_mcRun3_2021_realistic_v9-v2/50000/02f9c9a8-071c-4d30-ae1c-5c636c4dd8db.root',
            'root://cmsxrootd.fnal.gov///store/mc/Run3Winter22MiniAOD/DoubleElectron_FlatPt-1To500_13p6TeV/MINIAODSIM/FlatPU0to70_122X_mcRun3_2021_realistic_v9-v2/50000/f36892f2-58d9-41c4-80f7-55a34c4cc77c.root',
            ]
        elif options.isMC:                             pass # not implemented
        else:
            options.inputFiles = [
            'root://cms-xrd-global.cern.ch//store/data/Run2022D/ParkingDoubleElectronLowMass0/MINIAOD/10Dec2022-v2/2550000/017e91e2-36f3-41d0-aad5-aa8d2ba0d13a.root'
            ]

    elif options.year == 2022 and options.subera == 1: # POST-EE
        if options.isMC and options.isSignal:
            options.inputFiles = [ # not sure if these are pre/postEE
            'root://cmsxrootd.fnal.gov///store/user/marlow/EtaToGammaTM_TMToEE_2022/EtaToGammaTM_TMToEE_2022_MINIAOD_388.root', #1000 events
            'root://cmsxrootd.fnal.gov///store/user/marlow/EtaToGammaTM_TMToEE_2022/EtaToGammaTM_TMToEE_2022_MINIAOD_828.root',
            'root://cmsxrootd.fnal.gov///store/user/marlow/EtaToGammaTM_TMToEE_2022/EtaToGammaTM_TMToEE_2022_MINIAOD_60.root',
            'root://cmsxrootd.fnal.gov///store/user/marlow/EtaToGammaTM_TMToEE_2022/EtaToGammaTM_TMToEE_2022_MINIAOD_19.root',
            ]
        elif options.isMC and options.isMinBias:       pass # not implemented
        elif options.isMC and options.isPromptJpsi:    pass # not implemented
        elif options.isMC and options.isPromptUpsilon: pass # not implemented
        elif options.isMC:
            options.inputFiles = [
            'root://cmsxrootd.fnal.gov///store/mc/Run3Summer22EEMiniAODv4/BuToKJPsi_JPsiToEE_SoftQCD_TuneCP5_13p6TeV_pythia8-evtgen/MINIAODSIM/130X_mcRun3_2022_realistic_postEE_v6-v2/60000/aeb83042-4174-49e8-8d7e-3f4acfff0a13.root',
            'root://cmsxrootd.fnal.gov///store/mc/Run3Summer22EEMiniAODv4/BuToKJPsi_JPsiToEE_SoftQCD_TuneCP5_13p6TeV_pythia8-evtgen/MINIAODSIM/130X_mcRun3_2022_realistic_postEE_v6-v2/60000/f6f9d6d6-ecff-47a6-9d9c-f0be003d99b8.root',
            'root://cmsxrootd.fnal.gov///store/mc/Run3Summer22EEMiniAODv4/BuToKJPsi_JPsiToEE_SoftQCD_TuneCP5_13p6TeV_pythia8-evtgen/MINIAODSIM/130X_mcRun3_2022_realistic_postEE_v6-v2/60000/0c772889-596b-4358-aeef-8cef53dfe216.root',
            'root://cmsxrootd.fnal.gov///store/mc/Run3Summer22EEMiniAODv4/BuToKJPsi_JPsiToEE_SoftQCD_TuneCP5_13p6TeV_pythia8-evtgen/MINIAODSIM/130X_mcRun3_2022_realistic_postEE_v6-v2/60000/1223aeb1-1145-4a07-93ae-8ce5d5dd77dd.root',
            ] 
        else: 
            options.inputFiles = [
            'root://xrootd-cms.infn.it///store/data/Run2022G/ParkingDoubleElectronLowMass0/MINIAOD/22Sep2023-v1/70000/9100e1f2-e6fb-4ad3-9201-c421c75031b8.root',
            'root://xrootd-cms.infn.it///store/data/Run2022G/ParkingDoubleElectronLowMass0/MINIAOD/22Sep2023-v1/60000/4f3add8f-0e5d-4912-a551-1190126880d0.root',
            'root://xrootd-cms.infn.it///store/data/Run2022G/ParkingDoubleElectronLowMass0/MINIAOD/22Sep2023-v1/60000/72ae4983-b3a9-415d-a0fe-8255914514f0.root',
            'root://xrootd-cms.infn.it///store/data/Run2022G/ParkingDoubleElectronLowMass0/MINIAOD/22Sep2023-v1/60000/c2305f06-0a01-4ae4-bc3b-e56a83c8fc05.root',
            ]

    elif options.year == 2023 and options.subera == 0: # PRE-BPIX
        if options.isMC and options.isSignal:          pass # not implemented
        elif options.isMC and options.isMinBias:       pass # not implemented
        elif options.isMC and options.isPromptJpsi:
            options.inputFiles = [
            'root://xrootd-cms.infn.it///store/mc/Run3Summer23MiniAODv4/JPsiToEE_pth10toInf_TuneCP5_13p6TeV_pythia8/MINIAODSIM/130X_mcRun3_2023_realistic_v15-v2/140000/4e7a0372-833c-42b9-9b12-b66323d58da7.root',
            'root://xrootd-cms.infn.it///store/mc/Run3Summer23MiniAODv4/JPsiToEE_pth10toInf_TuneCP5_13p6TeV_pythia8/MINIAODSIM/130X_mcRun3_2023_realistic_v15-v2/140000/d17b2e6c-57b1-4847-a9b1-c4b499035a34.root',
            'root://xrootd-cms.infn.it///store/mc/Run3Summer23MiniAODv4/JPsiToEE_pth10toInf_TuneCP5_13p6TeV_pythia8/MINIAODSIM/130X_mcRun3_2023_realistic_v15-v2/140000/a9ff0f8a-a896-47b2-bd6b-c01a4778166c.root',
            'root://xrootd-cms.infn.it///store/mc/Run3Summer23MiniAODv4/JPsiToEE_pth10toInf_TuneCP5_13p6TeV_pythia8/MINIAODSIM/130X_mcRun3_2023_realistic_v15-v2/140000/ae1fbe5b-aed2-4eb3-bcb2-b36b748872fe.root',
            ]
        elif options.isMC and options.isPromptUpsilon: pass # not implemented
        elif options.isMC:                             pass # not implemented
        else:
            options.inputFiles = [
            'root://cms-xrd-global.cern.ch//store/data/Run2023C/ParkingDoubleElectronLowMass/MINIAOD/22Sep2023_v4-v1/2550000/004781d3-3b0c-4392-95fb-378e7859148a.root'
            ]

    elif options.year == 2023 and options.subera == 1: # POST-BPIX
        if options.isMC and options.isSignal:
            options.inputFiles = [ # not sure if these are pre/post-BPIX
            f'file:/eos/cms/store/cmst3/group/xee/signalSamples/HAHM_DarkPhoton_13p6TeV_Nov2024/HAHM_ZpToEE_012jets_VBF_INCLUSIVE_noVBFcuts_Leta1p22_LpT5_M5_k2e_4_eps0p05_13p6TeV_MINIAOD.root'
            ]
        elif options.isMC and options.isMinBias:       pass # not implemented
        elif options.isMC and options.isPromptJpsi:    pass # not implemented
        elif options.isMC and options.isPromptUpsilon:
            options.inputFiles = [
            'root://xrootd-cms.infn.it///store/mc/Run3Summer23BPixMiniAODv4/UpsilonToEE_pth10toInf_TuneCP5_13p6TeV_pythia8/MINIAODSIM/130X_mcRun3_2023_realistic_postBPix_v6-v2/140000/c269e0a6-3b8c-40de-a1bb-b922341b8475.root',
            'root://xrootd-cms.infn.it///store/mc/Run3Summer23BPixMiniAODv4/UpsilonToEE_pth10toInf_TuneCP5_13p6TeV_pythia8/MINIAODSIM/130X_mcRun3_2023_realistic_postBPix_v6-v2/140000/0b263174-e6e1-4697-9b48-399165df2b0a.root',
            'root://xrootd-cms.infn.it///store/mc/Run3Summer23BPixMiniAODv4/UpsilonToEE_pth10toInf_TuneCP5_13p6TeV_pythia8/MINIAODSIM/130X_mcRun3_2023_realistic_postBPix_v6-v2/140000/e1a5407d-cabf-4a6c-a416-b268701aa758.root',
            'root://xrootd-cms.infn.it///store/mc/Run3Summer23BPixMiniAODv4/UpsilonToEE_pth10toInf_TuneCP5_13p6TeV_pythia8/MINIAODSIM/130X_mcRun3_2023_realistic_postBPix_v6-v2/140000/5d574d53-dd86-4833-a4dd-fb38afef8428.root',
            ] 
        elif options.isMC:
            options.inputFiles = [
            'root://xrootd-cms.infn.it///store/mc/Run3Summer23BPixMiniAODv4/BuToKJPsi_JPsiToEE_SoftQCD_TuneCP5_13p6TeV_pythia8-evtgen/MINIAODSIM/130X_mcRun3_2023_realistic_postBPix_v2-v3/2820000/9bba4db3-9e00-4e97-b918-b4eda3059c15.root',
            'root://xrootd-cms.infn.it///store/mc/Run3Summer23BPixMiniAODv4/BuToKJPsi_JPsiToEE_SoftQCD_TuneCP5_13p6TeV_pythia8-evtgen/MINIAODSIM/130X_mcRun3_2023_realistic_postBPix_v2-v3/2820000/a4551d66-6e54-47de-94d1-72cbeee6ea4e.root',
            'root://xrootd-cms.infn.it///store/mc/Run3Summer23BPixMiniAODv4/BuToKJPsi_JPsiToEE_SoftQCD_TuneCP5_13p6TeV_pythia8-evtgen/MINIAODSIM/130X_mcRun3_2023_realistic_postBPix_v2-v3/2820000/4d776a87-a092-4c50-868b-34c54f040aa0.root',
            'root://xrootd-cms.infn.it///store/mc/Run3Summer23BPixMiniAODv4/BuToKJPsi_JPsiToEE_SoftQCD_TuneCP5_13p6TeV_pythia8-evtgen/MINIAODSIM/130X_mcRun3_2023_realistic_postBPix_v2-v3/2820000/a73d0ecd-1f89-4d62-b08b-d46362f6f2fb.root',
            ] 
        else:
            options.inputFiles = [
            'root://xrootd-cms.infn.it///store/data/Run2023D/ParkingDoubleElectronLowMass/MINIAOD/22Sep2023_v2-v1/2560000/95e1791e-7dec-499f-8a11-3ee133300eb5.root',
            'root://xrootd-cms.infn.it///store/data/Run2023D/ParkingDoubleElectronLowMass/MINIAOD/22Sep2023_v2-v1/2560000/12117d01-dc26-496c-9dcd-0c8310a008e3.root',
            'root://xrootd-cms.infn.it///store/data/Run2023D/ParkingDoubleElectronLowMass/MINIAOD/22Sep2023_v2-v1/2560000/c46bf23a-9284-4f7e-8d6b-7305fe7a9a70.root',
            'root://xrootd-cms.infn.it///store/data/Run2023D/ParkingDoubleElectronLowMass/MINIAOD/22Sep2023_v2-v1/2560000/f305f435-af66-4db3-ba8e-91ce02e6b431.root',
            ]
    elif options.year == 2024:
        if options.isMC and options.isSignal:
            options.inputFiles = [
            f'file:/eos/cms/store/cmst3/group/xee/signalSamples/HAHM_DarkPhoton_13p6TeV_Nov2024/HAHM_ZpToEE_MZp3_VBF_jetcut_ptj1_30_ptj2_30_lpt0p5_k1e_10_eps0p02_13p6TeV_50k_MINIAOD_2024.root'
            ]
        elif options.isMC and options.isMinBias:       pass # not implemented
        elif options.isMC and options.isPromptJpsi:    pass # not implemented
        elif options.isMC and options.isPromptUpsilon: pass # not implemented
        elif options.isMC:                             pass # not implemented
        else:
            options.inputFiles = [
            "root://cms-xrd-global.cern.ch//store/data/Run2024I/ParkingVBF1/MINIAOD/MINIv6NANOv15_v2-v3/90000/f6550b8f-2a31-4f6d-8ef8-1b513ad6abb1.root"
            ]


annotation = '%s nevts:%d' % (outputFileNANO, options.maxEvents)

# Process
from Configuration.StandardSequences.Eras import eras
from Configuration.Eras.Modifier_run3_nanoAOD_pre142X_cff import run3_nanoAOD_pre142X
from DoubleElectronNANO.BParkingNano.modifiers_cff import *

# Attaching modifiers
modifiers = []

# Do nano-v15 light for MiniAODv<6 (year<2024)
if options.year!=2024: modifiers.append(run3_nanoAOD_pre142X)

if options.mode not in ["reco", "eff", "trg", "vbf"]:
    raise ValueError("Mode must be reco (standard reconstruction), eff (efficiency study mode) or trg (trigger matching study mode)")

if options.mode == "eff":
    # Efficiency study:
    #     removes all selections among:
    #      - trigger selection (hltHighLevel filter)
    #      - electron selection (all selections inside electronsForAnalysis filter)
    #      - dielectron fit (both pre- and post-fit selections)
    #     Electron and dielectron-level selections are replaced by flags in the output,
    #     so that efficiency can be studied differentially separately.
    #     Trigger selection efficiency is evaluated using trgTable values.
    modifiers.append(efficiencyStudy)
elif options.mode == "trg":
    # Trigger matching study:
    #   removes all trigger selections and opens up deltaR max value for trigger-matching
    #   ambiguities not resolved -- looking at best match for each electron.
    modifiers.append(triggerMatchingStudy)
elif options.mode == "vbf":
    if options.year == 2022:
        raise ValueError("VBF parking was not active during 2022")
    elif options.year == 2023:
        if options.version == 'C':
            modifiers.append(vbfSkimming2023_C)
        else:
            modifiers.append(vbfSkimming2023_D)
    elif options.year == 2024:
        modifiers.append(vbfSkimming2024)

if options.saveRegressionVars:
    # Save regression variables
    # see python/electronsBPark_cff.py for list
    modifiers.append(regressionVars)

if options.isSignal:
    modifiers.append(allowedNumScaleWeights)

era=eras.Run3 if options.year==2022 else eras.Run3_2023 if options.year==2023 else eras.Run3_2024
process = cms.Process('BParkNANO', era, *modifiers)

# import of standard configurations
process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')
process.load('Configuration.StandardSequences.Services_cff')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration.EventContent.EventContent_cff')
process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load("Configuration.StandardSequences.MagneticField_cff")
process.load('PhysicsTools.NanoAOD.nano_cff')
process.load('DoubleElectronNANO.BParkingNano.nanoBPark_cff')
process.load('Configuration.StandardSequences.EndOfProcess_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')

process.MessageLogger.cerr.FwkReport.reportEvery = options.reportEvery
# process.MessageLogger.cerr.threshold = "DEBUG"
# process.MessageLogger.debugModules = ["*"]

process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(options.maxEvents)
)

# Input source
process.source = cms.Source(
    "PoolSource",
    fileNames = cms.untracked.vstring(options.inputFiles),
    secondaryFileNames = cms.untracked.vstring(),
    skipEvents=cms.untracked.uint32(options.skip),
)

process.options = cms.untracked.PSet(
    wantSummary = cms.untracked.bool(options.wantSummary),
)

process.nanoMetadata.strings.tag = annotation
# Production Info
process.configurationMetadata = cms.untracked.PSet(
    annotation = cms.untracked.string(annotation),
    name = cms.untracked.string('Applications'),
    version = cms.untracked.string('$Revision: 1.19 $')
)

# Output definition
process.FEVTDEBUGHLToutput = cms.OutputModule("PoolOutputModule",
    dataset = cms.untracked.PSet(
        dataTier = cms.untracked.string('GEN-SIM-RECO'),
        filterName = cms.untracked.string('')
    ),
    fileName = outputFileFEVT,
    outputCommands = (cms.untracked.vstring('keep *',
                                            'drop *_*_SelectedTransient*_*',
                     )),
    splitLevel = cms.untracked.int32(0)
)

process.NANOAODoutput = cms.OutputModule("NanoAODOutputModule",
    compressionAlgorithm = cms.untracked.string('LZMA'),
    compressionLevel = cms.untracked.int32(9),
    dataset = cms.untracked.PSet(
        dataTier = cms.untracked.string('NANOAOD'),
        filterName = cms.untracked.string('')
    ),
    fileName = outputFileNANO,
    outputCommands = cms.untracked.vstring(
      # 'drop *',
      "keep nanoaodFlatTable_*Table_*_*",     # event data
      "keep nanoaodUniqueString_nanoMetadata_*_*",   # basic metadata
      "keep nanoaodMergeableCounterTable_*Table_*_*", # run data
    )

)

# Additional output definition

# Other statements
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, globaltag, '')

from DoubleElectronNANO.BParkingNano.nanoBPark_cff import *
from DoubleElectronNANO.BParkingNano.electronsTrigger_cff import *

process = nanoAOD_customizeEgammaPostRecoTools(process)
process = nanoAOD_customizeEle(process)
process = nanoAOD_customizeElectronFilteredBPark(process)
if options.saveAllNanoContent:
    process = nanoAOD_customizeNanoContent(process)
    process = nanoAOD_customizeCommon(process)
process = nanoAOD_customizeTriggerBitsBPark(process)
process = nanoAOD_customizeElectronTriggerSelectionBPark(process)
process = nanoAOD_customizeDiElectron(process)

process.nanoAOD_DiEle_step = cms.Path(process.egammaPostRecoSeq
                                    + process.nanoSequence
                                    + process.nanoEleSequence
                                    + process.nanoDiEleSequence)

# customisation of the process.
if options.isMC:
    from DoubleElectronNANO.BParkingNano.nanoBPark_cff import nanoAOD_customizeMC
    nanoAOD_customizeMC(process, options.saveAllNanoContent)

process.endjob_step = cms.EndPath(process.endOfProcess)
process.FEVTDEBUGHLToutput_step = cms.EndPath(process.FEVTDEBUGHLToutput)
process.NANOAODoutput_step = cms.EndPath(process.NANOAODoutput)

# Schedule definition
process.schedule = cms.Schedule(process.nanoAOD_DiEle_step,
                                process.endjob_step,
                                process.NANOAODoutput_step)

if options.wantFullRECO:
    process.schedule = cms.Schedule(process.nanoAOD_DiEle_step,
                                    process.endjob_step,
                                    process.FEVTDEBUGHLToutput_step,
                                    process.NANOAODoutput_step)

from PhysicsTools.PatAlgos.tools.helpers import associatePatAlgosToolsTask
associatePatAlgosToolsTask(process)
process.NANOAODoutput.SelectEvents = cms.untracked.PSet(
    SelectEvents = cms.vstring('nanoAOD_DiEle_step')
)

### from https://hypernews.cern.ch/HyperNews/CMS/get/physics-validation/3287/1/1/1/1/1.html
process.add_(cms.Service('InitRootHandlers', EnableIMT = cms.untracked.bool(False)))
process.NANOAODoutput.fakeNameForCrab=cms.untracked.bool(True)

process.load("TrackingTools/TransientTrack/TransientTrackBuilder_cfi")
from Configuration.StandardSequences.earlyDeleteSettings_cff import customiseEarlyDelete
process = customiseEarlyDelete(process)
