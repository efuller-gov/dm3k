<template>
    <div id="graphContainer">
    </div>
</template>

<script>

  import {Dm3kGraph} from '../js/dm3kgraph/dm3kGraph';

  export default {
    name: 'GraphRenderer',
    data() {
      return {
        dm3kGraph: {}
      }
    },
    mounted() {
        this.loadDm3kGraph();
    },
    watch: {
        'this.$store.state.resources': function() {
            console.log("IN GRAPH RENDERER ", this.$store.state.resources)
        }
    },
    methods: {
        loadDm3kGraph() {
            console.log("Initializing graph...")
            this.dm3kGraph = new Dm3kGraph(document.querySelector('#graphContainer'))
        },
        // addResource(newResType, newResName, newBudgetNameList){
        //     this.dm3kGraph.addCompleteResource(newResType, newResName, newBudgetNameList)
        // }
    }
  };
// on graph store change, render resources
// let model = dm3kgraph.graph.getModel()
// if (model.getCell(newResName) != undefined){
//     alert('Cannot create duplicate node. Please choose a new instance name.')

// } else{
//     let ans = dm3kgraph.addCompleteResource(newResType, newResName, newBudgetNameList);

//     if (ans.success) {
//         console.log('AddResourceComplete success!')
//         updateAllDropDowns(dm3kgraph);
//         let layout = new mxGraphLayout(dm3kgraph.graph);
//         executeLayout(dm3kgraph.graph, layout);
//         resetResourcePrompt();
//     }
//     else {
//         alert(ans.details);
//     }
// }
</script>

<style scoped>
  .container {
    border-style: groove;
    border-width: thin;
    border-radius: 5px;
    height: 100%;
    width: 100%;
    padding: 5px;
    max-height: 72vh;
    max-width: 100%;
    overflow: hidden;
    border-color: grey;
    margin: 0px;
    transition: border-color 0.2s ease-in-out;
  }

  .container:hover {
    border-color: #242424;
  }

  #graphContainer {
    width: 100%;
    height: 100%;
    margin: 0px;
    padding: 0px;
    min-height: 72vh;
    overflow: hidden;
  }

  .float-tool-bar {
    position: relative;
    top: 0px;
    bottom: 0px;
    right: 0px;
    left: 0px;
    width: 40px;
    height: 200px;
    padding: 0;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }

  .tool-btn {
    width: 40px;
    height: 40px;
    border-radius: 999px;
    background: #f5f5f5;
    box-shadow: 0 2px 8px 0 #dcdcdc;
    display: flex;
    justify-content: center;
    align-items: center;
    cursor: pointer;
    margin-bottom: 5px;
    pointer-events: auto;
  }

  .menu-btn {
    background: transparent;
    transition: 0ms;
  }

  .overlapContainer {
    position: relative;
    width: 100%;
  }

  .buttonList {
    pointer-events: none;
    padding: 5px 0px 0px 5px;
    list-style-type: none;
    width: 100%;
    height: 100%;
    position: absolute;
    top: 0px;
    bottom: 0px;
    right: 0px;
    left: 0px;
    z-index: 1
  }

  li {
    pointer-events: none;
  }

  .textinfo {
    position: absolute;
    color: #b3b3b3;
    font-size: 14px;
    padding: 10px;
    bottom: 0px;
  }

</style>
