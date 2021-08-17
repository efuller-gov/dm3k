/**
 *  Module for converting Visual Diagrams into inputs for the DM3K backend
 */

/**
 * Convert a graph into a json form
 * 
 * @param {Dm3kGraph} dm3kgraph: an instance of the Dm3kGraph Class
 * @return {javascript object} outjson: the json form of the Dm3kGraph instance
 * 
 * {
	resourceClasses: [
		{
			className: <resourceClassName>,
			typeName: <resourceTypeName>,
			budgets: [<budgetName>, ...],
			containsClasses: [<otherResourceClassName>,...],
			canBeAllocatedToClasses: [<otherActivityClassName>, ...]
		},...],
	activityClasses: [
		{
			className:     <activityClassName>,
			typeName:     <activityTypeName>,
			rewards: [    <rewardName>, ...],
			costs: [    <budgetName>,...],
			containsClasses: [<otherActivityClassName>,...],
			allocatedWhen: {
				<rewardName>: {
					combine:     <AND|OR|NONE>,
					resource: [    <resourceClassName>, ...]
				},...
			}
		},...],
	resourceInstances: [
		{
			instanceName: <resourceInstanceName>,
			className: <resourceClassName>,
			budget: {
				<budgetName>: <budgetAmt>,...
			},
			contains: {
				<otherResourceClassName>: [<otherResourceInstanceName>,..], ...
			},
			canBeAllocatedTo: {
				<otherActivityClassName>: [<otherActivityInstanceName>,..], ...
			}
		},...],
	activityInstances: [
		{
			instanceName: <activityInstanceName>,
			className: <activityClassName>,
			cost: {
				<budgetName>: <costAmt>, ...
			},
			reward: {
				<rewardName>: <rewardAmt>, ...
			},
			contains: {
				<otherResourceClassName>: [<otherResourceInstanceName>,..],...
			}
		}, ...],
	allocationConstraints: [
		{
			allocationStart: {
				resourceClass:  <resourceClassName>,
				activityClass: <activityClassName>
			},
			allocationEnd: {
				resourceClass: <resourceClassName>,
				activityClass: <activityClassName>
			},
			allocationConstraintType: <Contained IF-THEN|IF-NOT|IF-ONLY>
		},...]
}
*/
export class Dm3kConverter {
	constructor() {
	}

	dm3kconversion_base(dm3kgraph) {
		var output = {};
		var final_output = {};
		output['resourceClasses'] = dm3kgraph.getResourceClassDetails();
		output['activityClasses'] = dm3kgraph.getActivityClassDetails();
		output['resourceInstances'] = [];   
		output['activityInstances'] = []; 
		output['allocationInstances'] = [];
		output['containsInstances'] = [];  
		output['allocationConstraints'] = dm3kgraph.getAllocationConstraintDetails();

		for (let ri of dm3kgraph.resourceInstances) {
			output['resourceInstances'] = output['resourceInstances'].concat(ri.getDetails());
		}

		for (let ai of dm3kgraph.activityInstances) {
			output['activityInstances'] = output['activityInstances'].concat(ai.getDetails());
		}

		for (let ci of dm3kgraph.containsInstances) {
			output['containsInstances'] = output['containsInstances'].concat(ci.getDetails());
		}

		for (let ai of dm3kgraph.allocatedToInstances) {
			output['allocationInstances'] = output['allocationInstances'].concat(ai.getDetails());
		}

		final_output['datasetName'] = ''
		final_output['files'] = []
		final_output['files'].push({
			fileName: '',
			fileContents: output
		})

		return final_output;
	}

	dm3kconversion_reverse(dm3kgraph, inputJson) {

		dm3kgraph.clearAll();  // this should get rid of all boxes and lines on graph
		console.log("Loading...")
		
		// add resource class boxes to diagram
		for (let rc of inputJson.resourceClasses) {
			
			// add the resource to the graph
			dm3kgraph.addCompleteResource(
				rc.typeName,
				rc.className,
				rc.budgets,
				rc.locX,
				rc.locY);
		}

		// add activity class boxes and canBeAllocated to links
		console.log("...activity classes...")
		console.log(inputJson.activityClasses)
		for (let ac of inputJson.activityClasses) {
			
			let actName = ac.className;
			console.log(actName)

			// determine which resources are allocated to this activity
			
			let resAllocList = []
			for (let rc of inputJson.resourceClasses) {
				var resName = rc.className;
				for (let cbat of rc.canBeAllocatedToClasses) {
					if (cbat == actName) {
						resAllocList.push(resName)
					}
				}
			}
			console.log(resAllocList)

			// add the activity and add any allocated to links
			for (let [i, ra] of resAllocList.entries()) {
				
				dm3kgraph.addCompleteActivity(
					ac.typeName,
					ac.className,
					ra,
					ac.rewards[0], // TODO - need to make it work for multiple rewards
					i,
					ac.locX,
					ac.locY,
				)
			}
		}

		console.log("...contains links - resources....");
		// add contains links - resources
		for (let rc of inputJson.resourceClasses) {
			let resName = rc.className;

			// NOTE - resources should always exist...so no need to do check like contains links - activities below

			for (let ccName of rc.containsClasses) {
				dm3kgraph.addContains(resName, ccName);
			}
		}

		console.log("...contains links - activities...");
		// add contains links - activities
		for (let ac of inputJson.activityClasses) {
			let actName = ac.className;

			// check to see if actName exists, if it doesnt...its a container activity
			let ai_dm3k = dm3kgraph.getActivityInstance(actName);
			if (ai_dm3k == undefined) {
				dm3kgraph.addNewActContains(
					ac.typeName, 
					actName, 
					ac.containsClasses[0],  // do the first one this way, then do rest in loop below
					ac.rewards[0]) // TODO - need to make it work for multiple rewards)
				for (let ccName of ac.containsClasses.slice(1)) {
					console.log('Attempting to make a contains link between: '+actName+' and '+ccName);
					dm3kgraph.addContains(actName, ccName);
					console.log(dm3kgraph.containsLinks)
				}
			}
			// else it is defined and therefore already available to add contains links to
			else {   
				for (let ccName of ac.containsClasses) {
					console.log('Attempting to make a contains link between: '+actName+' and '+ccName);
					dm3kgraph.addContains(actName, ccName);
					console.log(dm3kgraph.containsLinks)
				}
			}
			
		}
		
		console.log("...resource instances...");
		console.log(inputJson.resourceInstances)
		// Add resource instances
		for (let ri of inputJson.resourceInstances) {
			console.log(ri)
			let ri_name = ri.className;
			let ri_dm3k = dm3kgraph.getResourceInstance(ri_name);
			ri_dm3k.clearInstanceTable();
			for (let ri_instance of ri.instanceTable) {
				ri_dm3k.addToInstanceTable(ri_instance.instanceName, ri_instance.budget);
			}
		}

		console.log("...activity instances...");
		console.log(inputJson.activityInstances);
		// Add activity instances
		for (let ai of inputJson.activityInstances) {
			console.log(ai);
			let ai_name = ai.className;
			console.log(ai_name);
			console.log(dm3kgraph.activityInstances)
			let ai_dm3k = dm3kgraph.getActivityInstance(ai_name);
			ai_dm3k.clearInstanceTable();
			for (let ai_instance of ai.instanceTable) {
				ai_dm3k.addToInstanceTable(ai_instance.instanceName, ai_instance.reward, ai_instance.cost);
			}
		}

		console.log("...allocation instances...")
		console.log(inputJson.allocationInstances)
		// add allocation instances
		for (let ati of inputJson.allocationInstances) {
			let res_name = ati.resourceClassName;
			let act_name = ati.activityClassName;
			let ati_dm3k = dm3kgraph.getAllocatedToInstance(res_name, act_name);
			ati_dm3k.clearInstanceTable();
			for (let ati_instance of ati.instanceTable) {
				ati_dm3k.addToInstanceTable(ati_instance.resourceInstanceName, ati_instance.activityInstanceName);
			}
		}

		// add contains instances
		for (let ci of inputJson.containsInstances) {
			let parent_name = ci.parentClassName;
			let child_name = ci.childClassName;
			let ci_dm3k = dm3kgraph.getContainsInstance(parent_name, child_name);
			ci_dm3k.clearInstanceTable();
			for (let ci_instance of ci.instanceTable) {
				ci_dm3k.addToInstanceTable(ci_instance.parentInstanceName, ci_instance.childInstanceName);
			}
		}

		// add allocation constraints
		for (let allc of inputJson.allocationConstraints) {
			let a1FromName = allc.allocationStart.resourceClass;
			let a1ToName = allc.allocationStart.activityClass;
			let a2FromName = allc.allocationEnd.resourceClass;
			let a2ToName = allc.allocationEnd.activityClass;
			let aType = allc.allocationConstraintType;
			dm3kgraph.addConstraint(a1FromName, a1ToName, a2FromName, a2ToName, aType);
		}
		
	}
}