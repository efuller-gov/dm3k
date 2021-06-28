
import Vue from 'vue';
import Vuex from 'vuex';
import {AllocationInstance} from '../js/dm3kgraph/dataClasses';

Vue.use(Vuex);

export default new Vuex.Store({
  state: {
      resources : [],
      activities: [],
      allocatedLinks : [],
      containsLinks : [],
      constraints : [],
      resourceInstances : [],
      activityInstances : [],
      containsInstances : [],
      allocatedToInstances : [],
      rewards : {},
      budgets : {},
      costs : {}
},
  getters: {},
  mutations: {
    addResource(state, resourceObj) {
      state.resources.push(resourceObj)
      console.log("---- In STORE add res  ", state.resources)
    },
    addResourceInstance(state, resPayload){
      let resName = resPayload['instanceName']
      let resourceInstanceObj = resPayload['newInstance']
      console.log("---> in store, resPayload ", resPayload)
      console.log("state.resourceInstances ", state.resourceInstances)
      console.log("state.resourceInstances.filter(x=>x.label==resName)[0] ", state.resourceInstances.filter(x=>x.label==resName)[0])
      state.resourceInstances.filter(x=>x.label==resName)[0].instanceTableData.push(resourceInstanceObj)
      console.log("---- In STORE add res instnace ", state.resourceInstances)
    },
    addActivity(state, activityObj) {
      console.log("----> IN STORE, addActivity ", activityObj)
      state.activities.push(activityObj);
      // Add AllocationInstance when first create
      let ai = new AllocationInstance(activityObj['existingResName'], activityObj['actName']);
      console.log("ai ", ai)
      state.allocatedToInstances.push(ai);
    },
    addActivityInstance(state, actPayload){
      let actName = actPayload['instanceName']
      let activityInstanceObj = actPayload['newInstance']
      state.activityInstances.filter(x=>x.label==actName)[0].instanceTableData.push(activityInstanceObj)
    },
    addContainsLink(state, containsObj){
      state.containsLinks.push(containsObj);
    },
    addAllocation(state, allocObj) {
      state.allocatedLinks.push(allocObj);
      let ai = new AllocationInstance(allocObj['existingResName'], allocObj['actName']);
      state.allocatedToInstances.push(ai);
    },
    addCanBeAllocatedTo(state, allocObj){
      state.allocatedToInstances.filter(x=>(x.actName==allocObj['actName'] && x.resName==allocObj['existingResName']))[0].instanceTableData.push(
        { activityInstance: "ALL",
          resourceInstance: "ALL"}
      );
    },
    removeResourceInstance(state, resObj){
      state.resourceInstances.filter(x=>x.label==resObj['name'])[0]
    }
  },
  actions: {}
});