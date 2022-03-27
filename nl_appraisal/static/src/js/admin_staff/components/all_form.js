FullForm = {
  inject: ["appraisalData", "changeComponent"],
  data() {
    return {
      data: {},
    };
  },
  watch: {
    appraisalData: {
      handler(newVal, oldVal) {
        if (newVal.value) this.data = newVal.value;
      },
      immediate: true,
      deep: true,
    },
  },
  template: `
        <div>
            <a class="btn btn-secondary btn-sm btn-odoo" :href="'/report/pdf/nl_appraisal.report_employee_appraisal/' + data.id" v-if="data.metaInfo.state == 'done'">
                <i class="fa fa-view" /> 
                print
            </a>
            <button v-if="(['both_user', 'is_only_manager'].includes(appraisalData.value.manager_type) && appraisalData.value.state == 'final_comments')" @click="changeComponent('AppraisalStateReturner')" class="btn btn-secondary btn-sm btn-odoo">
                <i class="fa fa-view" /> 
                Move back to Supervisor Assessment
            </button>
            <div class="mt-4">
                <h4 style="margin-bottom:15px;">Employee Information</h4>
                <div class="row bg-white mt-2">
                    <div class="col-lg-2 headr py-1 px-2 headr custom_font_size" >Employee Name:</div>
                    <div class="col-lg-4 odoo-cell-grey py-1 px-2 custom_font_size">{{ data.employee_name }}</div>
                    <div class="col-lg-2 odoo-cell-grey py-1 px-2 headr custom_font_size">Emp. ID No.</div>
                    <div class="col-lg-4 odoo-cell-grey py-1 px-2 custom_font_size">{{ data.employee_idc_no }}</div>
                </div>
                <div class="row bg-white">
                    <div class="col-lg-2 headr py-1 px-2 headr custom_font_size">Position Title:</div>
                    <div class="col-lg-4 odoo-cell-grey py-1 px-2 custom_font_size">{{ data.position }}</div>
                    <div class="col-lg-2 odoo-cell-grey py-1 px-2 headr custom_font_size" >Office/Region:</div>
                    <div class="col-lg-4 odoo-cell-grey py-1 px-2 custom_font_size">{{ data.office }}</div>
                </div>
                <div class="row bg-white">
                    <div class="col-lg-2 headr py-1 px-2 headr custom_font_size" >Review Period:</div>
                    <div class="col-lg-4 odoo-cell-grey py-1 px-2 custom_font_size"> {{ data.from_date }} </div>
                    <div class="col-lg-6 odoo-cell-grey py-1 px-2 custom_font_size">{{ data.to_date }}</div>
                </div>
            </div>

            <div class="mt-5">
               <h4>General Objectives</h4>
                <div class="row bg-white mt-2">
                    <div class="headers">
                        <div class="col-lg-3 border-grey border py-1 px-2 headr" >Objective</div>
                        <div class="col-lg-2 border-grey border py-1 px-2 headr" >Expected Outcome</div>
                        <div class="col-lg-3 border-grey border py-1 px-2 headr" >Employee Feedback</div>
                        <div class="col-lg-3 border-grey border py-1 px-2 headr" >Manager Feedback</div>
                        <div class="col-lg-1 border-grey border py-1 px-2 headr" >Ratings</div>
                    </div>
                    <template v-for="obj in data.objectives">
                        <div class="col-lg-3 border-grey border py-1 odoo-cell-grey px-2 custom_font_size">{{ obj.name }}</div>
                        <div class="col-lg-2 border-grey border py-1 px-2 odoo-cell-grey custom_font_size">{{ obj.expected_outcome }}</div>
                        <div class="col-lg-3 border-grey border py-1 px-2 odoo-cell-grey custom_font_size">{{ obj.employee_feedback }}</div>
                        <div class="col-lg-3 border-grey border py-1 px-2 odoo-cell-grey custom_font_size">{{ obj.manager_feedback }}</div>
                        <div class="col-lg-1 border-grey border py-1 px-2 odoo-cell-grey rating custom_font_size">{{ obj.rating }}</div>
                    </template>
                <h4 style="margin-top:25px;">Learning Objectives</h4>
                    <div class="headers">
                        <div class="col-lg-3 border-grey border py-1 px-2 headr" >Individual Objective</div>
                        <div class="col-lg-4 border-grey border py-1 px-2 headr" >Employee Feedback</div>
                        <div class="col-lg-4 border-grey border py-1 px-2 headr" >Manager Feedback</div>
                        <div class="col-lg-1 border-grey border py-1 px-2 headr" >Rating</div>
                    </div>
                    <template v-for="obj in data.individual_objectives">
                        <div class="col-lg-3 border-grey border py-1 px-2 odoo-cell-grey custom_font_size">{{ obj.name }}</div>
                        <div class="col-lg-4 border-grey border py-1 px-2 odoo-cell-grey custom_font_size">{{ obj.employee_feedback }}</div>
                        <div class="col-lg-4 border-grey border py-1 px-2 odoo-cell-grey custom_font_size">{{ obj.manager_feedback }}</div>
                        <div class="col-lg-1 border-grey border py-1 px-2 odoo-cell-grey rating-learning custom_font_size">{{ obj.rating }}</div>
                    </template>
                </div>
            </div>

            <div class="mt-5" v-if="['objective_setting', 'performance_period'].indexOf(data.state) == -1">
                <h4 style="margin-bottom:25px;">Assessment of employee Technical and behavioral competencies during the period in review.</h4>
                <div class="row bg-white mt-2">
                    <div class="col-lg-12 border-grey question-box border py-1 px-2 custom_font_size" >1. How has the employee demonstrated their technical skills and competencies in the day-to-day work during the review period in terms of the professional skills, knowledge, accuracy of work, timelines and meeting deadlines and analysis of information for value addition to their work? Use specific examples where necessary</div>
                </div>
                <div class="row bg-white">
                    <div class="col-lg-2 py-1 px-2 custom_font_size left-side-box" >
                        <span>
                        Employee Comment
                        </span>
                    </div>
                    <div class="col-lg-10 py-1 px-2 odoo-cell-grey custom_font_size">{{ data.p3_q1_emp_comments }}</div>
                </div>
                <div class="row bg-white mt-3">
                    <div class="col-lg-2 py-1 px-2 custom_font_size left-side-box" >
                        <span>
                            Manager Comment
                        </span>
                    </div>
                    <div class="col-lg-10  py-1 px-2 odoo-cell-grey custom_font_size">{{ data.p3_q1_sup_comments }}</div>
                </div>
                <div class="row bg-white mt-2">
                    <div class="col-lg-12 border-grey border py-1 px-2 question-box custom_font_size" >2. How has the employee demonstrated their skills and competencies working with others through communication, coordination, and collaboration as a member of the team, supervisor, or line manager with the unit/department? Please cite examples and incidents</div>
                </div>
                <div class="row bg-white ">
                    <div class="col-lg-2 py-1 px-2 custom_font_size left-side-box" >
                        <span>
                            Employee Comment
                        </span>
                    </div>
                    <div class="col-lg-10 py-1 px-2 odoo-cell-grey custom_font_size">{{ data.p3_q2_emp_comments }}</div>
                </div>
                <div class="row bg-white mt-3">
                    <div class="col-lg-2  py-1 px-2 custom_font_size left-side-box" >
                        <span>
                            Manager Comment
                        </span>
                    </div>
                    <div class="col-lg-10  border py-1 px-2 no-border odoo-cell-grey custom_font_size">{{ data.p3_q2_sup_comments }}</div>
                </div>
                <div class="row bg-white mt-2">
                    <div class="col-lg-12  border py-1 px-2 question-box custom_font_size" >3. How has the employee proved their leadership ability to work independently, under pressure, leading through a crisis, adapting to changes  developing others through delegation and support?</div>
                </div>
                <div class="row bg-white ">
                    <div class="col-lg-2 py-1 px-2 custom_font_size left-side-box" >
                        <span>
                            Employee Comment
                        </span>
                    </div>
                    <div class="col-lg-10  py-1 px-2 odoo-cell-grey custom_font_size">{{ data.p3_q3_emp_comments }}</div>
                </div>
                <div class="row bg-white mt-3">
                    <div class="col-lg-2  py-1 px-2 custom_font_size left-side-box" >
                        <span>
                            Manager Comment
                        </span>
                    </div>
                    <div class="col-lg-10 py-1 px-2 odoo-cell-grey custom_font_size">{{ data.p3_q3_sup_comments }}</div>
                </div>
                <div class="row bg-white mt-2">
                    <div class="col-lg-12  py-1 px-2 question-box custom_font_size" >4. How has the employee integrated the SCA policies and values
                        <strong>(responsiveness, equality, impartiality, social justice and integrity)</strong> in the day-to-day work during the review period. Key pointers include gender, diversity and inclusion (GDI), enforcing and reinforcing policies, relationship building and support to colleagues, field teams, partners and key stakeholders etc.) Please cite specific examples that demonstrated application and integration of the values.
                    </div>
                </div>
                <div class="row bg-white">
                    <div class="col-lg-2  py-1 px-2 custom_font_size left-side-box" >
                        <span>
                            Employee Comment
                        </span>
                    </div>
                    <div class="col-lg-10  py-1 px-2 odoo-cell-grey custom_font_size" >{{ data.p3_q4_emp_comments }}</div>
                </div>
                <div class="row bg-white mt-3">
                    <div class="col-lg-2  py-1 px-2 custom_font_size left-side-box" >
                        <span>
                            Manager Comment
                        </span>
                    </div>
                    <div class="col-lg-10  py-1 px-2 odoo-cell-grey custom_font_size" >{{ data.p3_q4_sup_comments }}</div>
                </div>
            </div>

            <div class="mt-5" v-if="['objective_setting', 'performance_period'].indexOf(data.state) == -1">
                <h4 style="margin-bottom:25px;" >Employee Learning, Development and Career Aspirations</h4>
                <div class="row bg-white mt-2">
                    <div class="col-lg-6 border-grey border py-1 px-2 headr" >Guiding question</div>
                    <div class="col-lg-6 border-grey border py-1 px-2 headr" >Employee Feedback</div>
                </div>
                <div class="row bg-white">
                    <div class="col-lg-6 odoo-cell-grey py-1 px-2 custom_font_size" >Did you receive any formal training sponsored by SCA/Donor or stakeholder during the review period?</div>
                    <div class="col-lg-6 odoo-cell-grey py-1 px-2 custom_font_size">{{ data.p4_emp_feed1 }}</div>
                </div>
                <div class="row bg-white">
                    <div class="col-lg-6 odoo-cell-grey py-1 px-2 custom_font_size" >How has the training impacted on your work and SCA mission and objectives?</div>
                    <div class="col-lg-6 odoo-cell-grey py-1 px-2 custom_font_size">{{ data.p4_emp_feed2 }}</div>
                </div>
                <div class="row bg-white">
                    <div class="col-lg-6 odoo-cell-grey py-1 px-2 custom_font_size" >Where you involved in any assignments within your department/ unit? (out of your day-to-day work) such as Leading on a project, or any other assignment that improved your skills, competencies and confidence.</div>
                    <div class="col-lg-6 odoo-cell-grey py-1 px-2 custom_font_size">{{ data.p4_emp_feed3 }}</div>
                </div>
                <div class="row bg-white">
                    <div class="col-lg-6 odoo-cell-grey py-1 px-2 custom_font_size" >Do you think you are on the right career path in SCA? What are your career aspirations based on your skills, experience and current role in SCA?</div>
                    <div class="col-lg-6 odoo-cell-grey py-1 px-2 custom_font_size">{{ data.p4_emp_feed4 }}</div>
                </div>
                <div class="row bg-white mt-2">
                    <div class="col-lg-2  py-1 px-2 custom_font_size" >Employee Comment</div>
                    <div class="col-lg-10 odoo-cell-grey py-1 px-2 custom_font_size">{{ data.p4_emp_comments }}</div>
                </div>
                <div class="row bg-white mt-2 ">
                    <div class="col-lg-2 py-1 px-2 custom_font_size" >Manager Comments:</div>
                    <div class="col-lg-10  odoo-cell-grey py-1 px-2 custom_font_size">{{ data.p4_sup_comments }}</div>
                </div>
            </div>

            <div class="mt-5" v-if="['objective_setting', 'performance_period', 'self_review'].indexOf(data.state) == -1">
                <h4 style="margin-bottom:25px;">Performance Goals and Expectations (for next review period)</h4>
                <div class="row bg-white mt-2">
                    <div class="col-lg-6 headr py-1 px-2 headr custom_font_size " >
                        <strong>SMART GOALS: </strong>(Specific, Measurable, Attainable, Realistic, Timely)
                    </div>
                    <div class="col-lg-6 headr py-1 px-2 headr custom_font_size" >
                        <strong>Expected outcome/ How to know the objectives have been achieved.</strong>
                    </div>
                </div>
                <template v-for="obj in data.next_year_objectives">
                    <div class="row bg-white">
                        <div class="col-lg-6 odoo-cell-grey py-1 px-2 custom_font_size"> {{obj.name }}</div>
                        <div class="col-lg-6 odoo-cell-grey  py-1 px-2 custom_font_size">{{ obj.expected_outcome }}</div>
                    </div>
                </template>
                <div class="row bg-white mt-2">
                    <div class="col-lg-12 mt-2 headr py-1 px-2 headr" >Individual Development/ Learning Objectives - based on Training and Develpment needs and career aspirations.</div>
                </div>
                <div class="row bg-white">
                    <div class="col-lg-12 odoo-cell-grey py-1 px-2 custom_font_size" >
                        <strong style="color:black;">Identify one learning and development objective for the review period (Professional training, workshop/ seminar):</strong>
                        <p style="margin-top:25px;">{{ data.next_individual_obj1 }}</p>
                    </div>
                </div>
                <div class="row bg-white">
                    <div class="col-lg-12 odoo-cell-grey py-1 px-2 custom_font_size" >
                        <strong style="color:black;">Identify assignments and initiatives to support your career growth and aspirations within your unit or in SCA (Job shadowing Understudy, Project leading or back stopping):</strong>
                        <p style="margin-top:25px;">{{ data.next_individual_obj2 }}</p>
                    </div>
                </div>
            </div>

            <div class="mt-5" v-if="['objective_setting', 'performance_period'].indexOf(data.state) == -1">
                <h4 style="margin-bottom:25px;">Upward feedback to Supervisor/ Line manager</h4>
                <div class="row bg-white mt-2">
                    <div class="col-lg-6 custom_font_size custom_font_size headr py-1 px-2" >Employee feedback to the supervisor about how they feel they have been managed during the review period and any areas the supervisor could improve on.</div>
                    <div class="col-lg-6 custom_font_size custom_font_size odoo-cell-grey py-1 px-2" style="border:none !important;">{{ data.p6_emp_feed1 }}</div>
                </div>
            </div>

            <div class="mt-5" v-if="['objective_setting', 'performance_period', 'self_review'].indexOf(data.state) == -1">
                <h4 style="margin-bottom:25px;">Line Supervisor and overall performance rating and way forward</h4>
                <div class="row bg-white">
                    <div class="col-lg-3 headr custom_font_size border py-1 px-2" >
                        <strong>Rating</strong>
                    </div>
                    <div class="col-lg-6 headr  custom_font_size border py-1 px-2" >
                        <strong>Interpretaion</strong>
                    </div>
                    <div class="col-lg-3 headr  custom_font_size border py-1 px-2" >
                        <strong>Supervisor final rating</strong>
                    </div>
                </div>
                <div class="row">
                    <div class="col-lg-9 p-0">
                        <div class="row bg-white">
                            <div class="col-lg-4 odoo-cell-grey custom_font_size border py-1 px-2">4.5 – 5</div>
                            <div class="col-lg-8 odoo-cell-grey custom_font_size border py-1 px-2">Exceptional/Outstanding</div>
                        </div>
                        <div class="row bg-white">
                            <div class="col-lg-4 odoo-cell-grey custom_font_size border py-1 px-2">3.5 – 4.4</div>
                            <div class="col-lg-8 odoo-cell-grey custom_font_size border py-1 px-2">Exceeds Expected Performance</div>
                        </div>
                        <div class="row bg-white">
                            <div class="col-lg-4 odoo-cell-grey custom_font_size border py-1 px-2">2.5 – 3.4</div>
                            <div class="col-lg-8 odoo-cell-grey custom_font_size border py-1 px-2">Meets Expected Performance</div>
                        </div>
                        <div class="row bg-white">
                            <div class="col-lg-4 odoo-cell-grey custom_font_size border py-1 px-2">1.5 – 2.4 </div>
                            <div class="col-lg-8 odoo-cell-grey custom_font_size border py-1 px-2">Required performance improvement</div>
                        </div>
                        <div class="row bg-white">
                            <div class="col-lg-4 odoo-cell-grey custom_font_size border py-1 px-2">1 – 1.4 </div>
                            <div class="col-lg-8 odoo-cell-grey custom_font_size border py-1 px-2">Unsatisfactory/Unacceptable Performance</div>
                        </div>
                        <div class="row bg-white">
                            <div class="col-lg-4 odoo-cell-grey custom_font_size border py-1 px-2">Not Applicable</div>
                            <div class="col-lg-8 odoo-cell-grey custom_font_size border py-1 px-2">Not Applicable or Not Able to Evaluate</div>
                        </div>
                    </div>
                    <div class="col-lg-3 odoo-cell-grey custom_font_size">
                        <div class="d-flex justify-content-center align-items-center" style="height:100%; flex-direction:column; text-align:center;">
                            <span v-if="data.p7_overall_rating_not_applicable">Not Applicable</span>
                            <template v-else="">
                                <span style="font-size: 27px !important;
                                color: #875a7b;">{{data.p7_overall_rating}}</span>
                                <span class="mt-2" style="font-size:12px;">{{ data.p7_overall_rating >= 4.5 ? 'Exceptional/Outstanding' : data.p7_overall_rating >= 3.5 ? 'Exceeds Expected Performance' : data.p7_overall_rating >= 2.5 ? 'Meets Expected Performance' : data.p7_overall_rating >= 1.5 ? 'Required Performance Improvement' : data.p7_overall_rating >= 1 ? 'Unsatisfactory/Unacceptable Performance' : ''  }}</span>
                            </template>
                        </div>
                    </div>
                </div>
                <div class="bg-white border border-grey custom_font_size">
                    <div class="row">
                    <div class="col-lg-12 py-2 text-center font-weight-bold">Recommendation on employee contract with SCA (Cycle the applicable option)</div>
                </div>
                <div class="text-center py-1"> 
                    <span style="font-size: 18px !important;color: #875a7b;">
                        {{ data.contract_rec[data.p7_emp_contract_rec] }}
                    </span> 
                </div>
            </div>

            <div class="mt-5" v-if="['final_comments', 'done', 'cancel'].includes(data.state)">
                <h4 style="margin-bottom:25px;">2nd Line Manager/ Supervisor (If Applicable)</h4>
                <div class="row bg-white mb-2">
                    <div class="col-lg-6 headr custom_font_size py-1 px-2" >Do you agree with the above performance appraisal of the direct line manager?</div>
                    <div class="col-lg-6 odoo-cell-grey custom_font_size py-1 px-2" style="border: none !important;" >
                        {{ data.p8_2sup_q1 }}
                    </div>
                </div>
                <div class="row bg-white mb-2">
                    <div class="col-lg-6 headr custom_font_size py-1 px-2">
                        Reason
                        
                    </div>
                    <div class="col-lg-6 odoo-cell-grey custom_font_size border py-1 px-2" style="border: none !important;">
                    {{ data.p8_2sup_q1_reason }}
                    </div>
                </div>
                <div class="row bg-white mb-2">
                    <div class="col-lg-6 headr custom_font_size py-1 px-2">Are you directly familiar with this staff member's work?</div>
                    <div class="col-lg-6 odoo-cell-grey custom_font_size py-1 px-2" style="border: none !important;">
                        {{ data.p8_2sup_q2 }}
                    </div>
                </div>
            </div>

            <div class="mt-5" v-if="['done', 'cancel'].includes(data.state)">
                <h4 style="margin-bottom:25px;">Employee's feedback on rating and recommendations</h4>
                <div class="row bg-white">
                    <div class="col-lg-6 headr custom_font_size py-1 px-2" >
                        <p>Do you agree with the above performance appraisal rating and recommendation?</p>
                    </div>
                    <div class="col-lg-6 odoo-cell-grey custom_font_size py-1 px-2" style="border: none !important;" >
                        {{ data.p9_emp_feed  }}
                    </div>

                </div>
                <div class="row bg-white mt-2">
                    <div class="col-lg-6 headr custom_font_size py-1 px-2" >
                        Employee Comments
                    </div>
                    <div class="col-lg-6 odoo-cell-grey custom_font_size py-1 px-2" style="border: none !important;" >
                        <p>{{ data.p9_emp_feed_comments }}</p>
                    </div>
                </div>
    
                <p class="mt-2">(I understand that I am entitled to submit a statement of explanation if I so wish)</p>
                    
            </div>
            
            <div class="mt-5" v-if="data.employee_sign_date || data.manager_sign_date || data.second_manager_sign_date">
                <h3>Signed by:</h3>
                <div v-if="data.employee_sign_date">
                    <strong>Employee:</strong> {{ data.employee_name }} on {{ data.employee_sign_date }}
                </div>
                <div v-if="data.manager_sign_date">
                    <strong>Supervisor:</strong> {{ data.manager_name }} on {{ data.manager_sign_date }}
                </div>
                <div v-if="data.second_manager_sign_date">
                    <strong>2nd Supervisor (if applicable): </strong> {{ data.second_manager_name }} on {{ data.second_manager_sign_date }}
                </div>
            </div>

        </div>
        </div>
    `,
};
