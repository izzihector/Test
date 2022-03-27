MyFieldAppraisalParent = {
  props: ["id"],
  data() {
    return {
      currentComponent: "FieldFullForm",
      dataLoading: true,
      dataExists: false,
      appraisalData: {},
      error: false,
      message: "",
      messageType: "success",
      flash: false,
      hasAccess: true,
      hasAccessMessage: "",
    };
  },
  methods: {
    async getData() {
      try {
        result = await fetch("/employee/get-my-appraisal", {
          method: "POST",
          headers: {
            Accept: "application/json",
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ appraisal_id: this.id }),
        });
        jsonResponse = await result.json();
        if (jsonResponse.error) {
          throw new Error(
            `${jsonResponse.error.message} - ${jsonResponse.error.data.message}`
          );
        }
        this.appraisalData = JSON.parse(jsonResponse.result);
      } catch (e) {
        this.showMessage((message = e), (type = "error"));
      }
      this.dataLoading = false;
      if (Object.keys(this.appraisalData).length > 0) {
        this.dataExists = true;
        this.setAccessInfo();
      }
    },
    change_component(data) {
      this.currentComponent = data;
      this.setAccessInfo();
      this.toggleChat("block");
    },
    setAccessInfo() {
      this.hasAccess = this.appraisalData.metaInfo.hasCurrentComponentAccess;
      this.hasAccessMessage =
        this.appraisalData.metaInfo.hasCurrentComponentAccessMessage;
    },
    showMessage(message, type) {
      if (type == "error") {
        this.error = true;
      }
      this.message = message;
      this.messageType = type;
      this.flash = true;
    },
    closeMessage() {
      this.flash = false;
      this.message = "";
      this.messageType = "success";
      this.error = false;
    },
    toggleChat(val) {
      document.querySelector("#invoice_communication").style.display = val;
    },
  },
  provide() {
    return {
      appraisalData: Vue.computed(() => this.appraisalData),
      currentComponent: Vue.computed(() => this.currentComponent),
      toggleChat: this.toggleChat,
    };
  },
  components: {
    "side-bar": FieldSideBarComponent,
    FlashMessage,
    LoadingComponent,
    BreadCrumb,
    FieldFullForm,
  },
  mounted() {
    this.getData();
  },
  template: `
        <div class="row my-5">
            <BreadCrumb :state="appraisalData.field_state" v-if="!dataLoading && dataExists" appraisalType="fieldStaff"/>
            <div class="col-lg-3 py-5 pl-4 bg-white bd-right-grey" v-if="!dataLoading && dataExists  && hasAccess">
                <side-bar @change_component="change_component" sideBarType="managers" :access-data="appraisalData.metaInfo"/>
            </div>
            <div :class="{'col-lg-9': dataExists, 'col-lg-12': !dataExists || !hasAccess}" class="py-2 p-lg-5" style="background: white; min-height: 400px;">
                <template v-if="!dataLoading && dataExists">
                    <transition name="component-fade" mode="out-in">
                        <div class="alert custom_alert text-center d-block" v-if="!hasAccess">
                            {{ hasAccessMessage }}
                        </div>  
                    </transition>
                    <transition name="component-fade" mode="out-in">
                        <component :is="currentComponent" submit-type='byManager'></component>
                    </transition>
                </template>
                <LoadingComponent v-if="dataLoading && !error"/>
                <div v-if="!dataExists && !dataLoading && !error">
                    <h4>No Appraisal Record Found!</h4>
                </div>
            </div>
            <FlashMessage :message='message' v-if="flash" :type='messageType' @close-message='closeMessage' ></FlashMessage>
        </div>
    `,
};
const my_field_appraisal_app = Vue.createApp({});

my_field_appraisal_app.component(
  "single-field-appraisal-employee",
  MyFieldAppraisalParent
);
my_field_appraisal_app.mount("#vue_my_field_staff_appraisal_app");
