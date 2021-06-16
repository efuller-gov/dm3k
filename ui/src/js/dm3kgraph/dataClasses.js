/**
 *  Class definitions for instances of resources and activities.
 **/

export class AllocationInstance {

    constructor(resClassName, actClassName) {
        this.resName = resClassName;
        this.actName = actClassName;
        this.instanceTableData = [];
        this.addToInstanceTable('ALL', 'ALL')
    }

    addToInstanceTable(resInstanceName, actInstanceName) {
        this.instanceTableData.push({resourceInstance: resInstanceName,
                                     activityInstance: actInstanceName});
    }

    clearInstanceTable() {
        this.instanceTableData = [];
    }

    getDetails() {
        var detailList = {
            "resourceClassName": this.resName,
            "activityClassName": this.actName,
            "instanceTable": []
        };
        for (let instance of this.instanceTableData) {
            let details = {
                
                "resourceInstanceName": instance.resourceInstance,
                "activityInstanceName": instance.activityInstance 
            }
            detailList.instanceTable.push(details);
        }
        return detailList 
    }
}

export class ContainsInstance {

    constructor(parentName, childName, parentType) {
        this.parentName = parentName;
        this.childName = childName;
        this.parentType = parentType;
        this.instanceTableData = [];
        this.addToInstanceTable('ALL', 'ALL')
    }

    addToInstanceTable(parentInstanceName, childInstanceName) {
        this.instanceTableData.push({parentInstance: parentInstanceName,
                                     childInstance: childInstanceName});
    }

    clearInstanceTable() {
        this.instanceTableData = [];
    }

    getDetails() {
        var detailList = {
            "parentClassName": this.parentName,
            "childClassName": this.childName,
            "parentType": this.parentType,
            "instanceTable": []
        };
        for (let instance of this.instanceTableData) {
            let details = {
                
                "parentInstanceName": instance.parentInstance,
                "childInstanceName": instance.childInstance 
            }
            detailList.instanceTable.push(details);
        }
        return detailList 
    }
}

export class ResourceInstance {

     /**
      *  Define resource instance for storage and assignment to activities via UI.
      *
      **/

     constructor(type, label, budgetNameList) {

         this.type = type;
         this.label = label;
         this.budgetLabel = '';
         this.budgetValue = 0;
         this.budgetNameList = budgetNameList
         this.instanceTableData = [];
         this.edges = []; //activities the instance is allocated to
         this.allocated_to = 'ALL';
         let sample_name = ""+label+"_Resource_instance_0";
         this.addDefaultRow(sample_name)
         console.log("Resource Instance TableData: %O", this.instanceTableData)   
     }

    addDefaultRow(sample_name) {
        let instanceExample = {name: sample_name};
        for (const budgetName of this.budgetNameList) {
            instanceExample["budget_"+budgetName] = 1;
        }
        this.instanceTableData.push(instanceExample)
    }

    addToInstanceTable(sample_name, budgetDict) {
        let instanceExample = {name: sample_name};
        for (const budgetName in budgetDict) {
            instanceExample["budget_"+budgetName] = budgetDict[budgetName];
        }
        this.instanceTableData.push(instanceExample)
    }

    clearInstanceTable() {
        this.instanceTableData = [];
    }

    getDetails() {
        var detailList = {
            "className": this.label,
            "instanceTable": []
        }
        for (let instance of this.instanceTableData) {
            let details = {
                "instanceName": instance.name,
                "budget" : {}}
            for (let item in instance) {
                if (item.startsWith("budget")) {
                    let name = item.substring(7)  // 7 = size of 'budget_'
                    details.budget[name] = Number(instance[item]);
                }
            }
            detailList.instanceTable.push(details)
        }
        return detailList 
    }
}

export class ActivityInstance {

     /**
      *  Define activity instance for storage and assignment to activities via UI.
      *
      **/

    constructor(type, label, costNameList) {

         this.type = type;
         this.label = label;
         this.costNameList = costNameList;
         this.rewardLabel = '';
         this.rewardValue = 0;
         this.edges = []; //resource instances that are allocated to this activity instance
         let sample_name = ""+label+"_Activity_instance_0";
         this.instanceTableData = [];
         this.addDefaultRow(sample_name)

     }

    addDefaultRow(sample_name) {
        let instanceExample = {name: sample_name, reward: 1};
        for (const costName of this.costNameList) {
            instanceExample["cost_"+costName] = 1;
        }
        this.instanceTableData.push(instanceExample)
    }

    addToInstanceTable(sample_name, rewards, costDict) {
        let instanceExample = {name: sample_name, reward: rewards};
        for (const costName in costDict) {
            instanceExample["cost_"+costName] =costDict[costName];
        }
        this.instanceTableData.push(instanceExample)
    }

    clearInstanceTable() {
        this.instanceTableData = [];
    }

     getDetails() {
        var detailList = {
            "className": this.label,
            "instanceTable": []
        }
        for (let instance of this.instanceTableData) {
            let details = {
                
                "instanceName": instance.name,
                "cost" : {},    
                "reward": Number(instance.reward)  // TODO - fix this when we have mulitple rewards
            }
            for (let item in instance) {
                if (item.startsWith("cost")) {
                    let name = item.substring(5);  // 5 = size of 'cost_'
                    details.cost[name] = Number(instance[item]);
                }
            }
            
            detailList.instanceTable.push(details)
        }
        return detailList 
     }

}
