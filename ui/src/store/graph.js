
import Vue from 'vue';
import Vuex from 'vuex';

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
    },
    addResourceInstance(state, payload){
      let resName = payload['resName']
      let resourceInstanceObj = payload['newInstance']
      console.log("pushing ", resourceInstanceObj)
      state.resourceInstances.filter(x=>x.label==resName)[0].instanceTableData.push(resourceInstanceObj)
      console.log("FROM STORE state.resourceInstances ", state.resourceInstances)
    },
    addActivity(state, activityObj) {
      console.log("--> store addActivity: ")
      state.activities.push(activityObj);
      console.log("activityObj ", activityObj)
    },
    addAllocation(state, allocObj) {
      state.allocatedLinks.push(allocObj);
    }
  },
  actions: {}
});