SingleAppraisalEmployee = {
  props: ["id"],
  data() {
    return {
      currentComponent: "EObjectivesFeedback",
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
    async submitForm(data) {
      try {
        result = await fetch("/employee/update-my-appraisal", {
          method: "POST",
          headers: {
            Accept: "application/json",
            "Content-Type": "application/json",
          },
          body: JSON.stringify(data),
        });
        jsonResponse = await result.json();
        // ODOO Error catchh
        if (jsonResponse.error) {
          throw new Error(
            `${jsonResponse.error.message} - ${jsonResponse.error.data.message}`
          );
        }
        // Custom Error Catch
        responseData = JSON.parse(jsonResponse.result);
        if (responseData.update_status == "fail") {
          throw new Error(`${responseData.errors}`);
        }
        await this.getData();
        this.showMessage((message = "Saved Successfully!"), (type = "success"));
      } catch (e) {
        this.showMessage((message = e), (type = "error"));
        return false;
      }
      return true;
    },
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
        if (this.appraisalData.metaInfo.state == "final_comments") {
          this.change_component("EFinalComment");
        } else if (this.appraisalData.metaInfo.state != "self_review") {
          this.change_component("FullForm");
        }
        this.setAccessInfo();
      }
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
    toggleChat(val) {
      document.querySelector("#invoice_communication").style.display = val;
    },
  },
  provide() {
    return {
      appraisalData: Vue.computed(() => this.appraisalData),
      currentComponent: Vue.computed(() => this.currentComponent),
      changeComponent: this.change_component,
      submitFunction: this.submitForm,
      showFlashMessage: this.showMessage,
      closeFlashMessage: this.closeMessage,
      toggleChat: this.toggleChat,
    };
  },

  mounted() {
    this.getData();
  },
  components: {
    "side-bar": SideBarComponent,
    EObjectivesFeedback,
    ELearningObjectivesFeedback,
    ESelfAssessment,
    ECareerAspiration,
    EUpwardFeedback,
    EFinalComment,
    FlashMessage,
    LoadingComponent,
    BreadCrumb,
    SubmitForm,
    FullForm,
  },
  template: `
        <div style="width:100%; margin-top: -17px" v-if="!dataLoading && dataExists && ['self_review'].includes(appraisalData.state)">
            <div class="row bg-white mt-2">
                <div class="col-lg-2 border-grey border py-1 px-2 custom_font_size" >Employee Name:</div>
                <div class="col-lg-4 border-grey border py-1 px-2 custom_font_size">{{ appraisalData.employee_name }}</div>
                <div class="col-lg-2 border-grey border py-1 px-2 custom_font_size">Emp. ID No.</div>
                <div class="col-lg-4 border-grey border py-1 px-2 custom_font_size">{{ appraisalData.employee_idc_no }}</div>
            </div>
            <div class="row bg-white">
                <div class="col-lg-2 border-grey border py-1 px-2 custom_font_size">Position Title:</div>
                <div class="col-lg-4 border-grey border py-1 px-2 custom_font_size">{{ appraisalData.position }}</div>
                <div class="col-lg-2 border-grey border py-1 px-2 custom_font_size" >Office/Region:</div>
                <div class="col-lg-4 border-grey border py-1 px-2 custom_font_size">{{ appraisalData.office }}</div>
            </div>
            <div class="row bg-white">
                <div class="col-lg-4 border-grey border py-1 px-2 custom_font_size" >Review Period:</div>
                <div class="col-lg-4 border-grey border py-1 px-2 custom_font_size"> {{ appraisalData.from_date }} </div>
                <div class="col-lg-4 border-grey border py-1 px-2 custom_font_size">{{ appraisalData.to_date }}</div>
            </div>
        </div>
        <div class="row my-5">
            <BreadCrumb :state="appraisalData.state" v-if="!dataLoading && dataExists" appraisalType="adminStaff"/>
            <div style="border-top-left-radius: 5px;border-bottom-left-radius: 5px;border-right: 3px solid #ebebeb;" class="col-lg-3 py-5 pl-4 bg-white bd-right-grey" v-if="!dataLoading && dataExists &&  ['self_review'].includes(appraisalData.state)">
                <side-bar @change_component="change_component" :access-data="appraisalData.metaInfo"/>
            </div>
            <div :class="{'col-lg-9': dataExists, 'col-lg-12': !dataExists || ['self_review'].indexOf(appraisalData.state) == -1}" class="py-2 p-lg-5" style="background: #ffffff; min-height: 400px; position:relative;">
                <template v-if="!dataLoading && dataExists">
                    <transition name="component-fade" mode="out-in">
                        <div class="alert custom_alert text-center d-block" v-if="!hasAccess">
                            {{ hasAccessMessage }}
                        </div>  
                    </transition>
                    <transition name="component-fade" mode="out-in">
                        <component :is="currentComponent"  submit-type='byEmployee'></component>
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
const app = Vue.createApp({});
app.component("single-appraisal-employee", SingleAppraisalEmployee);
app.mount("#vue_my_appraisal_app");
