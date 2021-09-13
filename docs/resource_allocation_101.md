# Resource Allocation 101 #

[Resource Allocation](https://www.britannica.com/topic/operations-research/Resource-allocation) problems involve the distribution of resources among competing activities in order to maximize a reward.

The problem is to determine which/how many resources to allocate to which activity.  If more resources are available than needed, the solution indicates which resources are used and which are not.  Similarly, if there are more activities than can be done with available resources, the solution should indicate which activities are not performed, taking into account the associated costs and rewards.

Table of Contents:

[[_TOC_]]

## Defining a Problem ##

Resource Allocation problems have the following components:

* a set of resources, where each resource has an amount of budget to distribute
* a set of activities to be performed, where each activity consumes a specified amount of resources (aka cost) and provides some part of a reward
* indications defining which resources can be allocated to which activities.

> NOTE: the simplest example of a resource allocation problem is a *knapsack problem*.  For example, I'm going on a camping trip with a few friends.  Each friend has a backpack (**the resources**) that each can carry a certain amount of weight (**its budget**).  We have a number of camping items that we need to take (**the activities**).  Each camping item has a weight (**the cost**) and a value for making our trip a success (**the reward**). In this problem I want to know what camping items to take and who is carrying each item.  Therefore, specific camping items can be allocated to specific backpacks (**the indication of what can be allocated to**).

In order to define more complex resource allocation problems, we add the following additional components:

* indications defining which resources contain other resources (*this is important for understanding the total budget allocation for groups of resources*)
* indications defining which activities contain other activities (*this is important when rewards are associated with parent activities; such that rewards are only attained if all children activities of that parent are performed*)
* constraints on when an allocation of a resource to an activity can or can not be performed (*this is important when you have multiple resource and activity types that are interrelated in the real world*)

> NOTE: For a good example of contains indications, see */example/AllocationOfStaffToTasksUserStoriesCustomers.json* <br>  In this example, 'contains relationships' define how individual workers (resources) are grouped by specialty and by company AND define how tasks (activities) are grouped into user stories and grouped into customers that want a set of stories.  The customer reward is only received if all of a customer's user stories are achieved.

> NOTE: For a good example of constraints on allocations, see */example/AlienWorldDomination_wShip.json*  <br> In this example, constraints are used to ensure that the aliens can't shoot at a VIP (person the aliens want to kill) unless the turret that fires the missiles is pointed at the city in which the VIP is located.  This translates into the allocation constraint that a missile resource can only be allocated to a VIP activity if the turret resource is allocated to the City activity containing the VIP.

DM3K enables non-technical users to define resource allocation problems with our UI (for more information on how to define a problem in our UI see [*/docs/user_guide.md*](/docs/user_guide.md))

### Understanding the Difference Between Types and Instances ###

Part of defining a resource allocation problem is the concept of types (aka classes) and instances.

When initially defining your resource allocation problem, you start with defining the resource and activity types.

For example, say you want to plan the packing for your camping trip. You would have a type of resources called 'Backpacks' and a type of activities called 'Camping Items'.  

But there can be multiple camping items you might want to take on your camping trip and, if you are going with friends, you might have multiple backpacks.  These multiple possibilities are called *instances*.

So continuing with the example, I have 'George's Backpack' and 'Laura's Backpack' and 'Evan's Backpack' all as instances of the 'Backpacks' type.  I also can have 'sleeping bag', 'matches', 'cooking stove', 'rain gear', etc. as instances of the 'camping items' type.

When initially defining your resource allocation problem, you can also relate these resource and activity types by specifying that my resource type can be allocated to my activity type.

The 'can be allocated' indication is a "type" as well.  Therefore, the 'can be allocated' indication can have instances as well.  Instances for indications establish the specific relationships between instances of the resource and activity types.

So continuing with the example, say George really is worried about his camping stove and he is the only one who wants to carry it.  In this case an instance of the 'can be allocated' indication between the 'Backpacks' type and the 'Camping Items' type defines that the 'camping stove' instance can only be allocated to the 'George's Backpack' instance.

By leveraging *types* and *instances* you can abstract away detail in the formation of your resource allocation problem but also be able to drill down into detail when you want to define the specifics of your problem.

## Problem Component Definition and Detail ##

The following sections further define the components mentioned above.

### Resources ###

**Resources** are types of things you can allocate. Resources have **budgets**.

**Budgets** indicate the amount a resource can provide when allocated to an activity.  Budgets can be of different types.  A single resource type can have one or more budgets of different types (*e.g. a Backpack resource type could have a weight budget and a space budget*).

**Resources** can have one or more **Resource Instances** of that resource (*e.g. a 'Backpack' resource type could have instances including "George's backpack", "Laura's backpack", etc.*).  

Each **Resource Instances** can have a different **Budget** amount for each Budget Type (*e.g. "George's backpack" is small and has a 'weight' budget amount = 10 lbs and a 'space' budget amount = 1 cubic foot*).

### Activities ###

**Activities** are things you can allocate **Resources** to.  Activities have **Costs** and some have **Rewards**.

**Costs** establish how much of **Resource's** budget is required to perform this **Activity**

**Rewards** establish the benefit for allocating a **Resource** to this **Activity**.

**Activities** can have one or more **Activity Instances** of that activity (*e.g. a 'Camping Item' activity type could have instances including 'sleeping bag', 'matches', 'cooking stove', etc.*).

Each **Activity Instance** can have different **Cost** and **Reward** amounts. (*e.g. 'matches' have a 'weight' budget cost = 0.01 lbs, a 'space' cost amount = 0.001 cubic foot, and a reward = 10*)

### Can Be Allocated To Indications ###

**Can be Allocated To Indications** link **Resources** to **Activities** and define that 1 or more instances of the resource "CAN BE" allocated to 1 or more instances of the activity.

Each **Can be Allocated To Indication** can have one or more **Can be Allocated To Instances**.  These instances define that ALL **Resource Instances** or a specific **Resource Instance** can be allocated to ALL **Activity Instances** or a specific **Activity Instance**.  (*e.g. the 'camping stove' activity instance can be allocated to "George's Backpack", 'matches' can be allocated to ALL Backpacks, etc.*)

### Contains Indications ###

Some resources and activity types are in container (parent-child) relationships, where one resource or activity is said to contain another resource or activity.

**Contains Indications** link a parent type to a child type and define that 1 or more instances of the parent type contain 1 or more instances of the child type.

Each **Contains Indication** can have one or more **Contains Indication Instances**.  These instances define that ALL parent instances or a specific parent instance contain ALL child instances or a specific child instance.  (*e.g. the 'camping stove', 'matches', 'pot', and 'spaghetti'  activity instances are contained by the 'Cooking' activity instance in the newly created 'Camping Activities' Type*)

### Allocation Constraints ###

**Allocation Constraints** enable the user to constrain the ability of a **Can be Allocated To Indication**.  These constraints link two separate **Can be Allocated To Indications** to each other.

**Allocation Constraints** come in three flavors:
"Contains IF-THEN". "IF-NOT", and "IF ONLY". 


"Contained IF-THEN" allocation constraints work in conjunction with **Contains Indications** to tie the **Can be Allocated To Indication** from a parent resource and activity to a **Can be Allocated To Indication** between the children resource and activity.  Tying the parent allocation to the child allocation prevents the child **Can be Allocated To Indication** from working unless the first **Can be Allocated To Indication** includes allocations by parent instances that contain these children.  (*e.g. if I am on a ship with turrets that can be pointed at a city (parent relationship: turret resource allocated to city activity), I can't hit buildings with shells from the gun on that turret in another city (child relationship: shells resource allocated to buildings activity).  **Note- this assumes shells are a child resource of turret, and buildings a child activity of cities**).

"IF-NOT" allocation constraints prevent a **Resource Instances** from being allocated to more than one type of Activity.  (*e.g. if I am allocating grocery bags to different types of grocery items, and I don't want grocery items that are cleaning supplies to be in the same bag as food items, I can use an IF-NOT allocation constraint to enforce this*).

"IF-ONLY" allocation constraints are essentially the opposite of "IF-NOT";
they require a resource type to be allocated to one activity type before it can be allocated to another.  For example, a parent might impose on a knapsack problem the condition that before any dessert type items can be allocated, at least one health food type item must be allocated.  *Note*: this allocation constraint is not present in any of the current examples.
