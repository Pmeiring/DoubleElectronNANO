import uproot
import awkward as ak
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import os
import yaml
import process_root
import subprocess
import pickle
from Electron_Kinematics_Plotter import aggregate_data, plot_kinematics, plot_id, make_genflav_barplot
import WP_derivation

# source: https://github.com/cms-sw/cmssw/blob/c1b84d22fdf538675959e10095c0fc9b7c36cf6c/PhysicsTools/NanoAOD/plugins/CandMCMatchTableProducer.cc#L50-L57
flav_map = {0: 'unmatched', 
			1: 'prompt ele', 
			15: 'ele from prompt tau', 
			22: 'prompt photon', 
			5: 'ele from B', 
			4:'ele from c', 
			3: 'ele from light or unknown'}

plot_output_dir = '/Users/pmeiring/debugwp/DoubleElectronNANO/wp/img'


# root_dirs = {
	# '2022_2023_JPsiToEE_pth10toInf': 
	# [
	# 	'/eos/cms/store/group/cmst3/group/xee/tree_v1/backgroundSamples/allnanoColl/JPsiToEE_pth10toInf_TuneCP5_13p6TeV_pythia8/crab_JPsiToEE_pth10toInf_TuneCP5_13p6TeV_pythia8_2023BPix/251007_142912/0000/',
	# 	'/eos/cms/store/group/cmst3/group/xee/tree_v1/backgroundSamples/allnanoColl/JPsiToEE_pth10toInf_TuneCP5_13p6TeV_pythia8/crab_JPsiToEE_pth10toInf_TuneCP5_13p6TeV_pythia8_2022postEE/251024_130738/0000/'
	# ], 
	# '2022_2023_JPsiToEE_pth0to10_postBPix':
	# [
	# 	'/eos/cms/store/group/cmst3/group/xee/tree_v1/backgroundSamples/allnanoColl/JPsiToEE_pth0to10_TuneCP5_13p6TeV_pythia8/crab_JPsiToEE_pth0to10_TuneCP5_13p6TeV_pythia8_2022postEE/251024_130707/0000/',
	# 	'/eos/cms/store/group/cmst3/group/xee/tree_v1/backgroundSamples/allnanoColl/JPsiToEE_pth0to10_TuneCP5_13p6TeV_pythia8/crab_JPsiToEE_pth0to10_TuneCP5_13p6TeV_pythia8_2023BPix/251002_142838/0000/',
	# ],
	# '2022_2023_BuToKJpsi_Toee_postBPix':
	# [
	# 	'/eos/cms/store/group/cmst3/group/xee/tree_v1/backgroundSamples/allnanoColl/BuToKJPsi_JPsiToEE_SoftQCD_TuneCP5_13p6TeV_pythia8-evtgen/crab_BuToKJpsi_Toee_2022postEE_v2/251024_130643/0000',
	# 	'/eos/cms/store/group/cmst3/group/xee/tree_v1/backgroundSamples/allnanoColl/BuToKJPsi_JPsiToEE_SoftQCD_TuneCP5_13p6TeV_pythia8-evtgen/crab_BuToKJpsi_Toee_2022postEE_v6/251024_130632/0000',
	# 	'/eos/cms/store/group/cmst3/group/xee/tree_v1/backgroundSamples/allnanoColl/BuToKJPsi_JPsiToEE_SoftQCD_TuneCP5_13p6TeV_pythia8-evtgen/crab_BuToKJpsi_Toee_2023BPix/251002_142819/0000',
	# ],
	# '2022_2023_UpsilonToEE_pth0to10_postBPix':
	# [
	# 	'/eos/cms/store/group/cmst3/group/xee/tree_v1/backgroundSamples/allnanoColl/UpsilonToEE_pth0to10_TuneCP5_13p6TeV_pythia8/crab_UpsilonToEE_pth0to10_TuneCP5_13p6TeV_pythia8_2022postEE/251024_130800/0000',
	# 	'/eos/cms/store/group/cmst3/group/xee/tree_v1/backgroundSamples/allnanoColl/UpsilonToEE_pth0to10_TuneCP5_13p6TeV_pythia8/crab_UpsilonToEE_pth0to10_TuneCP5_13p6TeV_pythia8_2023BPix/251007_142925/0000',
	# ],
	# '2022_2023_UpsilonToEE_pth10toInf_postBPix':
	# [
	# 	'/eos/cms/store/group/cmst3/group/xee/tree_v1/backgroundSamples/allnanoColl/UpsilonToEE_pth10toInf_TuneCP5_13p6TeV_pythia8/crab_UpsilonToEE_pth10toInf_TuneCP5_13p6TeV_pythia8_2022postEE/251024_130822/0000',
	# 	'/eos/cms/store/group/cmst3/group/xee/tree_v1/backgroundSamples/allnanoColl/UpsilonToEE_pth10toInf_TuneCP5_13p6TeV_pythia8/crab_UpsilonToEE_pth10toInf_TuneCP5_13p6TeV_pythia8_2023BPix/251007_142939/0000',
	# ],
	# 'Bhagya_PromptJPsi_Samples':
	# [
	# 	# '/eos/cms/store/mc/Run3Summer23MiniAODv4/JPsiToEE_pth0to10_TuneCP5_13p6TeV_pythia8/MINIAODSIM/130X_mcRun3_2023_realistic_v15-v2/100000/055136d3-bf98-4e2b-b3e0-c732e7c47cfe.root',
	# 	# '/eos/cms/store/mc/Run3Summer23MiniAODv4/JPsiToEE_pth0to10_TuneCP5_13p6TeV_pythia8/MINIAODSIM/130X_mcRun3_2023_realistic_v15-v2/100000/05c8e58b-b4bd-4067-9fc3-899ccb58c563.root',
	# 	# '/eos/cms/store/mc/Run3Summer23MiniAODv4/JPsiToEE_pth0to10_TuneCP5_13p6TeV_pythia8/MINIAODSIM/130X_mcRun3_2023_realistic_v15-v2/100000/0d48d151-2dd4-44dd-bf94-2df844ca72be.root',
	# 	# '/eos/cms/store/mc/Run3Summer23MiniAODv4/JPsiToEE_pth0to10_TuneCP5_13p6TeV_pythia8/MINIAODSIM/130X_mcRun3_2023_realistic_v15-v2/100000/11cbb431-ba38-4de6-946e-18b133660e46.root',
	# 	# '/eos/cms/store/mc/Run3Summer23MiniAODv4/JPsiToEE_pth0to10_TuneCP5_13p6TeV_pythia8/MINIAODSIM/130X_mcRun3_2023_realistic_v15-v2/100000/152f83df-329d-455f-b6cd-cdb359cf51e4.root',
	# 	# '/eos/cms/store/mc/Run3Summer23MiniAODv4/JPsiToEE_pth0to10_TuneCP5_13p6TeV_pythia8/MINIAODSIM/130X_mcRun3_2023_realistic_v15-v2/100000/184d427f-8dbb-4db1-a510-458965c44f58.root',
	# 	# '/eos/cms/store/mc/Run3Summer23MiniAODv4/JPsiToEE_pth0to10_TuneCP5_13p6TeV_pythia8/MINIAODSIM/130X_mcRun3_2023_realistic_v15-v2/100000/1979c76b-1d30-4a0e-b5d2-a20961e61d22.root',
	# 	# '/eos/cms/store/mc/Run3Summer23MiniAODv4/JPsiToEE_pth0to10_TuneCP5_13p6TeV_pythia8/MINIAODSIM/130X_mcRun3_2023_realistic_v15-v2/100000/19d9c655-1fbb-4dc5-85b3-4a110b2583db.root',
	# 	# '/eos/cms/store/mc/Run3Summer23MiniAODv4/JPsiToEE_pth0to10_TuneCP5_13p6TeV_pythia8/MINIAODSIM/130X_mcRun3_2023_realistic_v15-v2/100000/1c2ae1c8-4704-475b-bbef-60107f821692.root',
	# 	# '/eos/cms/store/mc/Run3Summer23MiniAODv4/JPsiToEE_pth0to10_TuneCP5_13p6TeV_pythia8/MINIAODSIM/130X_mcRun3_2023_realistic_v15-v2/100000/1cf0a568-c286-449e-ac3b-65d9459027c5.root',
	# 	# '/eos/cms/store/mc/Run3Summer23MiniAODv4/JPsiToEE_pth0to10_TuneCP5_13p6TeV_pythia8/MINIAODSIM/130X_mcRun3_2023_realistic_v15-v2/100000/1db9e92f-e913-436c-a4b4-1d835333dfec.root',
	# 	# '/eos/cms/store/mc/Run3Summer23MiniAODv4/JPsiToEE_pth0to10_TuneCP5_13p6TeV_pythia8/MINIAODSIM/130X_mcRun3_2023_realistic_v15-v2/100000/1e51cdd1-9db8-45c9-914b-8f42fc2bd62b.root',
	# 	# '/eos/cms/store/mc/Run3Summer23MiniAODv4/JPsiToEE_pth0to10_TuneCP5_13p6TeV_pythia8/MINIAODSIM/130X_mcRun3_2023_realistic_v15-v2/100000/26dc6017-47c8-4d41-b3d5-6249ef5db06e.root',
	# 	# '/eos/cms/store/mc/Run3Summer23MiniAODv4/JPsiToEE_pth0to10_TuneCP5_13p6TeV_pythia8/MINIAODSIM/130X_mcRun3_2023_realistic_v15-v2/100000/274efecd-80e7-4db3-8960-3850f2b6311a.root',
	# 	# '/eos/cms/store/mc/Run3Summer23MiniAODv4/JPsiToEE_pth0to10_TuneCP5_13p6TeV_pythia8/MINIAODSIM/130X_mcRun3_2023_realistic_v15-v2/100000/2a402d72-1b85-4e71-b5cf-478297d9984b.root',
	# 	# '/eos/cms/store/mc/Run3Summer23MiniAODv4/JPsiToEE_pth0to10_TuneCP5_13p6TeV_pythia8/MINIAODSIM/130X_mcRun3_2023_realistic_v15-v2/100000/2a508317-b0dd-44d8-9afa-29a10797b2f1.root',
	# 	# '/eos/cms/store/mc/Run3Summer23MiniAODv4/JPsiToEE_pth0to10_TuneCP5_13p6TeV_pythia8/MINIAODSIM/130X_mcRun3_2023_realistic_v15-v2/100000/2bc7dc7c-6561-491b-83ed-1877e3ec7935.root',
	# 	# '/store/mc/Run3Summer23MiniAODv4/JPsiToEE_pth0to10_TuneCP5_13p6TeV_pythia8/MINIAODSIM/130X_mcRun3_2023_realistic_v15-v2/100000/2f316968-d0bd-48a1-b9b3-0c541f5a89d3.root',
	# 	# '/store/mc/Run3Summer23MiniAODv4/JPsiToEE_pth0to10_TuneCP5_13p6TeV_pythia8/MINIAODSIM/130X_mcRun3_2023_realistic_v15-v2/100000/33ffca85-549e-4d95-95d5-9e0d8ef8034c.root',
	# 	# '/store/mc/Run3Summer23MiniAODv4/JPsiToEE_pth0to10_TuneCP5_13p6TeV_pythia8/MINIAODSIM/130X_mcRun3_2023_realistic_v15-v2/100000/340b1b71-76fd-4882-a448-7b671ae2c466.root',
	# 	# '/store/mc/Run3Summer23MiniAODv4/JPsiToEE_pth0to10_TuneCP5_13p6TeV_pythia8/MINIAODSIM/130X_mcRun3_2023_realistic_v15-v2/100000/3ab19408-4a7d-4b9c-b5dc-8b3a0b84a330.root',
	# 	# '/store/mc/Run3Summer23MiniAODv4/JPsiToEE_pth0to10_TuneCP5_13p6TeV_pythia8/MINIAODSIM/130X_mcRun3_2023_realistic_v15-v2/100000/3ba4e639-6089-45e9-af4a-3aa09434d29d.root',
	# 	# '/store/mc/Run3Summer23MiniAODv4/JPsiToEE_pth0to10_TuneCP5_13p6TeV_pythia8/MINIAODSIM/130X_mcRun3_2023_realistic_v15-v2/100000/4162877b-494f-4c5e-b914-33f52b0dbd81.root',
	# 	# '/store/mc/Run3Summer23MiniAODv4/JPsiToEE_pth0to10_TuneCP5_13p6TeV_pythia8/MINIAODSIM/130X_mcRun3_2023_realistic_v15-v2/100000/46492e91-ab4e-4cb7-a6da-4cdca33a984a.root',
	# 	# '/store/mc/Run3Summer23MiniAODv4/JPsiToEE_pth0to10_TuneCP5_13p6TeV_pythia8/MINIAODSIM/130X_mcRun3_2023_realistic_v15-v2/100000/476e5e91-3391-4374-95b5-e43f19e29179.root',
	# 	# '/store/mc/Run3Summer23MiniAODv4/JPsiToEE_pth0to10_TuneCP5_13p6TeV_pythia8/MINIAODSIM/130X_mcRun3_2023_realistic_v15-v2/100000/47d4d61b-4bac-4974-b85b-17e7e2350005.root',
	# 	# '/store/mc/Run3Summer23MiniAODv4/JPsiToEE_pth0to10_TuneCP5_13p6TeV_pythia8/MINIAODSIM/130X_mcRun3_2023_realistic_v15-v2/100000/4821c5ee-161f-4f19-8e16-82a6205fd55d.root',
	# 	# '/store/mc/Run3Summer23MiniAODv4/JPsiToEE_pth0to10_TuneCP5_13p6TeV_pythia8/MINIAODSIM/130X_mcRun3_2023_realistic_v15-v2/100000/4a14d253-3e6a-4cda-9395-44cd46e96cf5.root',
	# 	# '/store/mc/Run3Summer23MiniAODv4/JPsiToEE_pth0to10_TuneCP5_13p6TeV_pythia8/MINIAODSIM/130X_mcRun3_2023_realistic_v15-v2/100000/4b54e865-878c-4076-894c-4804cae1d352.root',
	# 	# '/store/mc/Run3Summer23MiniAODv4/JPsiToEE_pth0to10_TuneCP5_13p6TeV_pythia8/MINIAODSIM/130X_mcRun3_2023_realistic_v15-v2/100000/4c7e378a-682b-428e-9e0b-c7d8de51e78b.root',
	# 	# '/store/mc/Run3Summer23MiniAODv4/JPsiToEE_pth0to10_TuneCP5_13p6TeV_pythia8/MINIAODSIM/130X_mcRun3_2023_realistic_v15-v2/100000/5440942f-72bd-4232-98ce-8aa952219af3.root',
	# 	# '/store/mc/Run3Summer23MiniAODv4/JPsiToEE_pth0to10_TuneCP5_13p6TeV_pythia8/MINIAODSIM/130X_mcRun3_2023_realistic_v15-v2/100000/5a76b425-1b9b-4193-96b8-044c8560dcf5.root',
	# 	# '/store/mc/Run3Summer23MiniAODv4/JPsiToEE_pth0to10_TuneCP5_13p6TeV_pythia8/MINIAODSIM/130X_mcRun3_2023_realistic_v15-v2/100000/613bfe55-13a3-43e2-bd9a-a84db5df6075.root',
	# 	# '/store/mc/Run3Summer23MiniAODv4/JPsiToEE_pth0to10_TuneCP5_13p6TeV_pythia8/MINIAODSIM/130X_mcRun3_2023_realistic_v15-v2/100000/660762f4-307e-488e-a5e4-978bdbcd1b55.root',
	# 	# '/store/mc/Run3Summer23MiniAODv4/JPsiToEE_pth0to10_TuneCP5_13p6TeV_pythia8/MINIAODSIM/130X_mcRun3_2023_realistic_v15-v2/100000/66dba9ca-aa0e-4c01-87fe-585278c3581c.root',
	# 	# '/store/mc/Run3Summer23MiniAODv4/JPsiToEE_pth0to10_TuneCP5_13p6TeV_pythia8/MINIAODSIM/130X_mcRun3_2023_realistic_v15-v2/100000/6b7a72aa-61b0-42bb-bc91-74ddd25b4239.root',
	# 	# '/store/mc/Run3Summer23MiniAODv4/JPsiToEE_pth0to10_TuneCP5_13p6TeV_pythia8/MINIAODSIM/130X_mcRun3_2023_realistic_v15-v2/100000/6c26be1b-24d8-445a-8e46-58422519160b.root',
	# 	# '/store/mc/Run3Summer23MiniAODv4/JPsiToEE_pth0to10_TuneCP5_13p6TeV_pythia8/MINIAODSIM/130X_mcRun3_2023_realistic_v15-v2/100000/7152a3c8-2d16-46ff-a3e3-ab40d1197b21.root',
	# 	# '/store/mc/Run3Summer23MiniAODv4/JPsiToEE_pth0to10_TuneCP5_13p6TeV_pythia8/MINIAODSIM/130X_mcRun3_2023_realistic_v15-v2/100000/72823f27-47d9-470a-bc98-62d3f8bb7e23.root',
	# 	# '/store/mc/Run3Summer23MiniAODv4/JPsiToEE_pth0to10_TuneCP5_13p6TeV_pythia8/MINIAODSIM/130X_mcRun3_2023_realistic_v15-v2/100000/7453dd8e-4aa9-41b1-bc95-ee837fca7e84.root',
	# 	# '/store/mc/Run3Summer23MiniAODv4/JPsiToEE_pth0to10_TuneCP5_13p6TeV_pythia8/MINIAODSIM/130X_mcRun3_2023_realistic_v15-v2/100000/8011c229-35b0-42e0-bf77-6cb7c07d7109.root',
	# 	# '/store/mc/Run3Summer23MiniAODv4/JPsiToEE_pth0to10_TuneCP5_13p6TeV_pythia8/MINIAODSIM/130X_mcRun3_2023_realistic_v15-v2/100000/86502309-83a0-4168-b47d-17aee742d37d.root',
	# 	# '/store/mc/Run3Summer23MiniAODv4/JPsiToEE_pth0to10_TuneCP5_13p6TeV_pythia8/MINIAODSIM/130X_mcRun3_2023_realistic_v15-v2/100000/869474ce-f796-4a5b-a7bb-a619f0989ba9.root',
	# 	# '/store/mc/Run3Summer23MiniAODv4/JPsiToEE_pth0to10_TuneCP5_13p6TeV_pythia8/MINIAODSIM/130X_mcRun3_2023_realistic_v15-v2/100000/8696babc-15bc-49a4-942c-48a92908c868.root',
	# 	# '/store/mc/Run3Summer23MiniAODv4/JPsiToEE_pth0to10_TuneCP5_13p6TeV_pythia8/MINIAODSIM/130X_mcRun3_2023_realistic_v15-v2/100000/86f15951-5e22-45c8-9780-9b85866170d0.root',
	# 	# '/store/mc/Run3Summer23MiniAODv4/JPsiToEE_pth0to10_TuneCP5_13p6TeV_pythia8/MINIAODSIM/130X_mcRun3_2023_realistic_v15-v2/100000/8f0fb1c8-6a6d-48de-8a3e-20876993a349.root',
	# 	# '/store/mc/Run3Summer23MiniAODv4/JPsiToEE_pth0to10_TuneCP5_13p6TeV_pythia8/MINIAODSIM/130X_mcRun3_2023_realistic_v15-v2/100000/9a50ee3b-6ad6-4a45-877a-713098fc885f.root',
	# 	# '/store/mc/Run3Summer23MiniAODv4/JPsiToEE_pth0to10_TuneCP5_13p6TeV_pythia8/MINIAODSIM/130X_mcRun3_2023_realistic_v15-v2/100000/9ab38f1e-adf9-4fbd-b4ca-60501372f1a7.root',
	# 	# '/store/mc/Run3Summer23MiniAODv4/JPsiToEE_pth0to10_TuneCP5_13p6TeV_pythia8/MINIAODSIM/130X_mcRun3_2023_realistic_v15-v2/100000/ad8f4267-f34d-445d-9112-258e39e8ed44.root',
	# 	# '/store/mc/Run3Summer23MiniAODv4/JPsiToEE_pth0to10_TuneCP5_13p6TeV_pythia8/MINIAODSIM/130X_mcRun3_2023_realistic_v15-v2/100000/af8f8a57-44a5-4f7d-b669-bef91f8c8d14.root'
	# ]
# }

def main():
	sample_yaml = 'sample.yaml'
	plot_output_dir = '/eos/user/m/mkanemur/WebEOS/WorkingPoint'
	
	## Open a pikle file
	pkl_fname = 'processed/HAHM_VBF_processed.pkl'
	with open(pkl_fname, 'rb') as file:
		data = pickle.load(file)
	dataset_name = pkl_fname.split('/')[1].split('.')[0].replace('_processed', '') ## i.e., HAHM_VBF

	key_list = list(data.keys())
	print(key_list)
	print(data[key_list[0]].keys())
	print(data[key_list[0]]['data'].keys())

	electron_vars = ['Electron_pt', 'Electron_eta', 'Electron_phi', 'Electron_isLowPt', 
	'Electron_isPF', 'Electron_isPFoverlap', 'Electron_genPartFlav', 'Electron_genPartIdx', 
	'GenPart_statusFlags', 'GenPart_pdgId', 'GenPart_status', 'Electron_lowPtID_10Jun2025', 
	'Electron_PFEleMvaID_Run3CustomJpsitoEEValue', 'Electron_PFEleMvaID_Winter22NoIsoV1Value']

	## goal: get a signal/bkg where Electron_genPartFlav == 1, 12, 22
	mass_points = list(data.keys()) ## M1, M3p1, etc
	for mass_point in mass_points:
		total_events = data[mass_point]['total_entries']
		available_vals = list(data[mass_point]['data'].keys()) ## Electron_pt, Electron_eta, Electron_genPartFlav etc

		electrons = {var: data[mass_point]['data'].get(var) for var in electron_vars}

		if electrons['Electron_pt'] is None or electrons['Electron_genPartFlav'] is None:
			print(f'Missing Electron_pt or Electron_genPartFlav in {mass_point}')
			continue

		## set up signal and background
		flav = electrons['Electron_genPartFlav']
		signal_mask = (flav == 1) | (flav == 15) | (flav == 22)
		bkg_mask = ~signal_mask
		
		signal, background = {}, {}

		for var, arr in electrons.items():
			sig = arr[signal_mask]
			bkg = arr[bkg_mask]

			sig_np = ak.to_numpy(ak.flatten(sig))
			bkg_np = ak.to_numpy(ak.flatten(bkg))
			signal[var] = sig_np
			background[var] = bkg_np

		## Each variable is stored as np array
		data[mass_point]['data']['signal'] = signal
		data[mass_point]['data']['background'] = background
		print(f"{mass_point}: signal = {len(signal['Electron_pt'])}, background = {len(background['Electron_pt'])}")


	aggregated_signal_data, aggregated_background_data = aggregate_data(data)
	# make_genflav_barplot(aggregated_signal_data, aggregated_background_data, dataset_name, f'{plot_output_dir}/{dataset_name}')
	

	WP_derivation.main(aggregated_signal_data, aggregated_background_data)

	####### Plot kinematic vars #######
	# vars_to_plot = {'Electron_pt': (0, 20), 'Electron_eta': (-3, 3), 'Electron_phi': (-3, 3)}
	# vars_to_plot = {
					#  'Electron_lowPtID_10Jun2025': (-10, 10), 
					# 'Electron_PFEleMvaID_Run3CustomJpsitoEEValue': (-10, 10),
					# 'Electron_PFEleMvaID_Winter22NoIsoV1Value': (-1, 1)
					# }
	# params = {
	# 	'sig_data': aggregated_signal_data, 
	# 	'bkg_data': aggregated_background_data, 
	# 	'plot_vars': vars_to_plot, 
	# 	'dataset_name': dataset_name, 
	# 	'output_dir': f'{plot_output_dir}/{dataset_name}'
	# }
	# plot_kinematics(**params)

	####### plot IDs #######
	# vars_to_plot = {
	# 'Electron_lowPtID_10Jun2025': [(-20, 20), -1000], 
	# 				'Electron_PFEleMvaID_Run3CustomJpsitoEEValue': [(-11, 11), 20], 
					# 'Electron_PFEleMvaID_Winter22NoIsoV1Value': [(-1.2, 1.2), 20]}
	# params = {
	# 	'sig_data': aggregated_signal_data, 
	# 	'bkg_data': aggregated_background_data, 
	# 	'plot_vars': vars_to_plot, 
	# 	'dataset_name': dataset_name, 
	# 	'output_dir': f'{plot_output_dir}/{dataset_name}',
	# 	'log_scale': True
	# }
	# plot_id(**params)

if __name__ == "__main__":
	main()


	